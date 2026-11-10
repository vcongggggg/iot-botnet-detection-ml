# -*- coding: utf-8 -*-
"""
Pipeline Machine Learning cho bài toán Phát hiện Xâm nhập Mạng IoT (IoT-NIDS)
trên Bộ dữ liệu Chuẩn quốc tế Stratosphere IoT-23 (Zeek / Bro conn.log format).

Đồng bộ 100% với Notebook 01 và Mô hình Đóng gói (iot_nids_bundle.joblib):
- Sử dụng ĐÚNG 12 đặc trưng luồng mạng (9 số học + 3 phân loại).
- Loại bỏ hoàn toàn các trường định danh tĩnh: 'ts', 'uid', 'id.orig_h', 'id.resp_h',
  'local_orig', 'local_resp', 'service', 'missed_bytes', 'tunnel_parents'.
- Mặc định đọc TOÀN BỘ dữ liệu (hỗ trợ tùy chọn --rows để giới hạn mẫu khi kiểm thử).
"""

import os
import sys
import time
import argparse
import joblib
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


# Danh sách cột chuẩn của Zeek conn.log
ZEEK_COLUMNS = [
    'ts', 'uid', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p',
    'proto', 'service', 'duration', 'orig_bytes', 'resp_bytes',
    'conn_state', 'local_orig', 'local_resp', 'missed_bytes',
    'history', 'orig_pkts', 'orig_ip_bytes', 'resp_pkts',
    'resp_ip_bytes', 'tunnel_parents', 'label', 'detailed-label'
]

# Chuẩn mực 12 đặc trưng khớp tuyệt đối với bundle và notebook 01/02
NUMERIC_FEATURES = [
    'id.orig_p', 'id.resp_p', 'duration', 'orig_bytes', 'resp_bytes',
    'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes'
]
CATEGORICAL_FEATURES = ['proto', 'conn_state', 'history']
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_iot23_data(file_path: str, max_rows: int = None) -> pd.DataFrame:
    """
    Đọc dữ liệu IoT-23 từ file CSV hoặc file nguyên bản conn.log.labeled.
    Mặc định đọc TOÀN BỘ dữ liệu nếu max_rows=None.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    row_desc = f"{max_rows:,} dòng" if max_rows else "toàn bộ dữ liệu"
    print(f"[*] Đang tải dữ liệu từ {file_path} ({row_desc})...")
    start = time.time()

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, nrows=max_rows, low_memory=False)
    else:
        df = pd.read_csv(
            file_path,
            sep=r'\s+',
            comment='#',
            names=ZEEK_COLUMNS,
            nrows=max_rows,
            low_memory=False
        )

    print(f"[+] Đã load {len(df):,} dòng dữ liệu trong {time.time() - start:.2f}s.")
    return df


def preprocess_data(df: pd.DataFrame, binary_mode: bool = True):
    """
    Tiền xử lý dữ liệu IoT-23 chuẩn 12 đặc trưng:
    - Thay thế ký tự missing '-' và '(empty)' của Zeek thành 0.
    - Ép kiểu 9 cột số học về float32.
    - Label Encoding cho 3 biến phân loại ('proto', 'conn_state', 'history').
    - Chuẩn hóa nhãn mục tiêu (Benign=0, Malicious=1).
    """
    print("[*] Đang tiền xử lý dữ liệu theo chuẩn 12 đặc trưng...")
    df = df.copy()

    # 1. Chuẩn hóa nhãn target
    if 'label' in df.columns:
        target_col = 'label'
    elif 'detailed-label' in df.columns:
        target_col = 'detailed-label'
    elif 'Label' in df.columns:
        target_col = 'Label'
    else:
        target_col = df.columns[-1]

    print(f"[*] Cột nhãn mục tiêu: {target_col}")
    labels = df[target_col].astype(str).str.strip()

    if binary_mode:
        y = labels.apply(lambda x: 0 if 'benign' in x.lower() else 1).values
        class_names = ['Benign (0)', 'Malicious (1)']
    else:
        le_target = LabelEncoder()
        y = le_target.fit_transform(labels)
        class_names = [str(c) for c in le_target.classes_]

    # 2. Xử lý 12 đặc trưng features
    feature_cols = []
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = df[col].replace('-', 0).replace('(empty)', 0)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(np.float32)
            feature_cols.append(col)

    encoders = {}
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].replace('-', 'UNKNOWN').replace('(empty)', 'UNKNOWN').astype(str)
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
            feature_cols.append(col)

    X = df[feature_cols].values
    print(f"[+] Số lượng đặc trưng trích xuất: {len(feature_cols)} cột: {feature_cols}")
    print(f"[+] Phân bố nhãn: Benign={np.sum(y == 0):,}, Malicious={np.sum(y == 1):,}")

    return X, y, feature_cols, encoders, class_names


def train_and_evaluate(X, y, class_names):
    """
    Huấn luyện và đối sánh 5 mô hình Machine Learning theo Stratified 80/20.
    """
    print("\n[*] Chia tách phân tầng: Train (80%) và Test độc lập (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=500, random_state=42),
            "use_scaled": True
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(max_depth=16, random_state=42),
            "use_scaled": False
        },
        "Random Forest": {
            "model": RandomForestClassifier(n_estimators=70, max_depth=14, n_jobs=-1, random_state=42),
            "use_scaled": False
        },
        "XGBoost": {
            "model": xgb.XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                eval_metric='logloss', random_state=42, n_jobs=-1, tree_method='hist'
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
    print("\n" + "="*84)
    print(f"{'MÔ HÌNH':<22} | {'ACCURACY':<10} | {'PRECISION':<10} | {'RECALL':<10} | {'F1-SCORE':<10} | {'TRAIN TIME':<10}")
    print("="*84)

    best_lgbm = None

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

        avg_mode = 'binary' if len(class_names) == 2 else 'weighted'
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

        if name == "LightGBM":
            best_lgbm = clf

        print(f"{name:<22} | {acc*100:>8.2f}% | {prec*100:>8.2f}% | {rec*100:>8.2f}% | {f1*100:>8.2f}% | {train_time:>8.2f}s")

    print("="*84)
    results_df = pd.DataFrame(results)
    return results_df, best_lgbm, scaler


def main():
    parser = argparse.ArgumentParser(description="Pipeline Train & Đánh giá IoT-23 Intrusion Detection (12 Đặc trưng)")
    parser.add_argument("--data", type=str, default=None, help="Đường dẫn tới file dataset (.csv hoặc .labeled)")
    parser.add_argument("--rows", type=int, default=None, help="Số lượng dòng đọc vào (Mặc định: None - đọc toàn bộ)")
    parser.add_argument("--multiclass", action="store_true", help="Chạy phân loại đa lớp (mặc định là nhị phân)")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_set_path = os.path.join(base_dir, "train_set.csv")
    sample_file = os.path.join(base_dir, "sample_test_data", "sample_test_flows_5000.csv")

    if args.data:
        data_path = args.data
    elif os.path.exists(train_set_path):
        data_path = train_set_path
    elif os.path.exists(sample_file):
        data_path = sample_file
    else:
        raise FileNotFoundError("Không tìm thấy dữ liệu huấn luyện!")

    df = load_iot23_data(data_path, max_rows=args.rows)
    X, y, feature_cols, encoders, class_names = preprocess_data(df, binary_mode=not args.multiclass)

    results_df, model, scaler = train_and_evaluate(X, y, class_names)

    report_path = os.path.join(base_dir, "benchmark_results.csv")
    results_df.to_csv(report_path, index=False)
    print(f"\n[+] Đã lưu kết quả benchmark vào: {report_path}")


if __name__ == "__main__":
    main()
