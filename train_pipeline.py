"""
Pipeline Machine Learning cho bai toan Phat hien Xam nhap Mang IoT (IoT-NIDS)
tren Bo du lieu IoT-23 (Zeek / Bro conn.log.labeled format hoac Kaggle CSV format).

Cac chuc nang:
1. Parse conn.log.labeled (Zeek format) hoac doc file CSV.
2. Data Preprocessing & Cleaning (xu ly '-' thanh NaN, fillna, label encoding).
3. Train nhieu mo hinh: Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM.
4. Danh gia toan dien (Accuracy, Precision, Recall, F1, Confusion Matrix, Classification Report).
5. Xuat bang so sanh truc quan Markdown / CSV va luu model tot nhat.
"""

import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb


# Danh sach cot chuan cua Zeek conn.log
ZEEK_COLUMNS = [
    'ts', 'uid', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p',
    'proto', 'service', 'duration', 'orig_bytes', 'resp_bytes',
    'conn_state', 'local_orig', 'local_resp', 'missed_bytes',
    'history', 'orig_pkts', 'orig_ip_bytes', 'resp_pkts',
    'resp_ip_bytes', 'tunnel_parents', 'label', 'detailed-label'
]

# Cac dac trung so hoc va phan loai co ich cho viec hoc
NUMERIC_FEATURES = [
    'id.orig_p', 'id.resp_p', 'duration', 'orig_bytes', 'resp_bytes',
    'missed_bytes', 'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes'
]
CATEGORICAL_FEATURES = ['proto', 'service', 'conn_state', 'history']


def load_iot23_data(file_path: str, max_rows: int = 200000) -> pd.DataFrame:
    """
    Doc du lieu IoT-23 tu file CSV hoac file goc conn.log.labeled.
    Tu dong nhan dien dinh dang file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Khong tim thay file: {file_path}")

    print(f"[*] Dang tai du lieu tu {file_path} (max_rows={max_rows})...")
    start = time.time()

    # Kiem tra xem co phai file CSV khong
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, nrows=max_rows, low_memory=False)
    else:
        # File Zeek conn.log.labeled thuong phan cach boi tab hoac space va bat dau boi dau '#'
        df = pd.read_csv(
            file_path,
            sep=r'\s+',
            comment='#',
            names=ZEEK_COLUMNS,
            nrows=max_rows,
            low_memory=False
        )

    print(f"[+] Da load {len(df):,} dong du lieu trong {time.time() - start:.2f}s.")
    return df


def preprocess_data(df: pd.DataFrame, binary_mode: bool = True):
    """
    Tien xu ly du lieu IoT-23:
    - Thay the ky tu '-' (missing cua Zeek) thanh 0 hoac NaN.
    - Ep kieu cac cot so ve float.
    - Label Encoding cho cac bien phan loai.
    - Chuan hoa nhan (Target Label).
    """
    print("[*] Dang tien xu ly du lieu...")
    df = df.copy()

    # 1. Chuan hoa nhan target
    target_col = None
    if 'label' in df.columns:
        target_col = 'label'
    elif 'detailed-label' in df.columns:
        target_col = 'detailed-label'
    elif 'Label' in df.columns:
        target_col = 'Label'
    else:
        # Chon cot cuoi cung neu khong thay ten
        target_col = df.columns[-1]

    print(f"[*] Cot nhan muc tieu: {target_col}")

    # Chuan hoa chuoi nhan
    labels = df[target_col].astype(str).str.strip()

    if binary_mode:
        # Binary: Benign (0) vs Malicious (1)
        # Nhan 'Benign' hoac chua tu 'benign' -> 0, con lai -> 1
        y = labels.apply(lambda x: 0 if 'benign' in x.lower() else 1).values
        class_names = ['Benign (0)', 'Malicious (1)']
    else:
        # Multi-class
        le_target = LabelEncoder()
        y = le_target.fit_transform(labels)
        class_names = [str(c) for c in le_target.classes_]

    # 2. Xu ly cac dac trung features
    feature_cols = []
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            # Zeek dung '-' cho gia tri null
            df[col] = df[col].replace('-', 0).replace('(empty)', 0)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            feature_cols.append(col)

    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].replace('-', 'UNKNOWN').replace('(empty)', 'UNKNOWN')
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            feature_cols.append(col)

    X = df[feature_cols].values
    print(f"[+] So luong dac trung trich xuat: {len(feature_cols)} cot: {feature_cols}")
    print(f"[+] Phan bo nhan: {np.bincount(y)}")

    return X, y, feature_cols, class_names


def train_and_evaluate(X, y, class_names):
    """
    Train 5 mo hinh Machine Learning khac nhau va so sanh hieu nang.
    """
    print("\n[*] Chia tap Train (80%) va Test (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Chuan hoa du lieu (can thiet cho Logistic Regression)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Dinh nghia cac mo hinh
    models = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=500, random_state=42),
            "use_scaled": True
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(max_depth=12, random_state=42),
            "use_scaled": False
        },
        "Random Forest": {
            "model": RandomForestClassifier(n_estimators=100, max_depth=15, n_jobs=-1, random_state=42),
            "use_scaled": False
        },
        "XGBoost": {
            "model": xgb.XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                eval_metric='logloss', random_state=42, n_jobs=-1
            ),
            "use_scaled": False
        },
        "LightGBM": {
            "model": lgb.LGBMClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                random_state=42, n_jobs=-1, verbose=-1
            ),
            "use_scaled": False
        }
    }

    results = []

    print("\n" + "="*80)
    print(f"{'MO HINH':<22} | {'ACCURACY':<10} | {'PRECISION':<10} | {'RECALL':<10} | {'F1-SCORE':<10} | {'TRAIN TIME':<10}")
    print("="*80)

    for name, config in models.items():
        clf = config["model"]
        is_scaled = config["use_scaled"]
        X_tr = X_train_scaled if is_scaled else X_train
        X_te = X_test_scaled if is_scaled else X_test

        start_time = time.time()
        clf.fit(X_tr, y_train)
        train_time = time.time() - start_time

        start_eval = time.time()
        y_pred = clf.predict(X_te)
        eval_time = time.time() - start_eval

        # Tinh cac metrics
        is_binary = len(class_names) == 2
        avg_mode = 'binary' if is_binary else 'weighted'

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average=avg_mode, zero_division=0)
        rec = recall_score(y_test, y_pred, average=avg_mode, zero_division=0)
        f1 = f1_score(y_test, y_pred, average=avg_mode, zero_division=0)

        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "Train_Time_s": train_time,
            "Inference_Time_s": eval_time
        })

        print(f"{name:<22} | {acc*100:>8.2f}% | {prec*100:>8.2f}% | {rec*100:>8.2f}% | {f1*100:>8.2f}% | {train_time:>8.2f}s")

    print("="*80)

    results_df = pd.DataFrame(results)
    return results_df


def generate_synthetic_iot23_sample(output_csv: str, n_samples: int = 50000):
    """
    Sinh mau du lieu mo phong dung dinh dang Zeek conn.log cua IoT-23
    de chay thu nghiem ngay khi nguoi dung chua tai xong file 8.8GB.
    """
    print(f"[*] Dang tao mau du lieu test gia lap ({n_samples:,} dong)...")
    np.random.seed(42)

    protocols = ['tcp', 'udp', 'icmp']
    services = ['-', 'http', 'dns', 'ssh', 'dhcp', 'ssl']
    conn_states = ['S0', 'SF', 'OTH', 'REJ', 'RSTO', 'RSTR']
    history_patterns = ['S', 'ShADadFf', 'D', 'Dd', 'ShAdfFa']

    is_attack = np.random.choice([0, 1], size=n_samples, p=[0.35, 0.65])

    data = {
        'ts': np.random.uniform(1530000000, 1540000000, n_samples),
        'uid': [f'C{i:08x}' for i in range(n_samples)],
        'id.orig_h': ['192.168.1.195' if a else f'192.168.1.{np.random.randint(2, 50)}' for a in is_attack],
        'id.orig_p': np.random.randint(1024, 65535, n_samples),
        'id.resp_h': [f'10.0.0.{np.random.randint(1, 255)}' for _ in range(n_samples)],
        'id.resp_p': np.where(is_attack == 1, np.random.choice([23, 2323, 80, 443, 8080], n_samples), np.random.randint(1, 65535, n_samples)),
        'proto': np.random.choice(protocols, n_samples, p=[0.75, 0.22, 0.03]),
        'service': np.random.choice(services, n_samples),
        'duration': np.where(is_attack == 1, np.random.exponential(0.1, n_samples), np.random.exponential(5.0, n_samples)),
        'orig_bytes': np.where(is_attack == 1, np.random.randint(0, 100, n_samples), np.random.randint(50, 5000, n_samples)),
        'resp_bytes': np.where(is_attack == 1, np.zeros(n_samples), np.random.randint(0, 15000, n_samples)),
        'conn_state': np.where(is_attack == 1, np.random.choice(['S0', 'REJ'], n_samples), np.random.choice(conn_states, n_samples)),
        'local_orig': '-',
        'local_resp': '-',
        'missed_bytes': np.zeros(n_samples),
        'history': np.random.choice(history_patterns, n_samples),
        'orig_pkts': np.where(is_attack == 1, np.random.randint(1, 4, n_samples), np.random.randint(5, 50, n_samples)),
        'orig_ip_bytes': np.random.randint(40, 2000, n_samples),
        'resp_pkts': np.where(is_attack == 1, np.zeros(n_samples), np.random.randint(1, 40, n_samples)),
        'resp_ip_bytes': np.random.randint(0, 5000, n_samples),
        'tunnel_parents': '-',
        'label': np.where(is_attack == 1, 'Malicious', 'Benign'),
        'detailed-label': np.where(is_attack == 1, np.random.choice(['PartOfAHorizontalPortScan', 'Okiru', 'DDoS', 'C&C'], n_samples), '-')
    }

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"[+] Da tao xong file test sample: {output_csv}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Pipeline Train & Danh gia IoT-23 Intrusion Detection")
    parser.add_argument("--data", type=str, default=None, help="Duong dan toi file dataset (.csv hoac .labeled)")
    parser.add_argument("--rows", type=int, default=100000, help="So luong dong doc vao (tranh tran RAM)")
    parser.add_argument("--multiclass", action="store_true", help="Chay phan loai da lop (mac dinh la nhi phan)")
    parser.add_argument("--generate-sample", action="store_true", help="Sinh sample test de chay thu pipeline ngay")
    args = parser.parse_args()

    sample_file = "c:\\Study\\HocKy6\\IoT_NIDS_Pipeline\\iot23_sample.csv"

    if args.generate_sample or (args.data is None and not os.path.exists(sample_file)):
        generate_synthetic_iot23_sample(sample_file, n_samples=50000)
        data_path = sample_file
    else:
        data_path = args.data if args.data else sample_file

    df = load_iot23_data(data_path, max_rows=args.rows)
    X, y, feature_cols, class_names = preprocess_data(df, binary_mode=not args.multiclass)

    results_df = train_and_evaluate(X, y, class_names)

    # Luu ket qua danh gia
    report_path = "c:\\Study\\HocKy6\\IoT_NIDS_Pipeline\\benchmark_results.csv"
    results_df.to_csv(report_path, index=False)
    print(f"\n[+] Da luu bang so sanh ket qua vao: {report_path}")


if __name__ == "__main__":
    main()

