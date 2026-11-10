# -*- coding: utf-8 -*-
"""
Script tính toán ROC và AUC THẬT cho cả 5 mô hình Machine Learning trên tập kiểm thử độc lập.
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng
Nhóm 4: Nguyễn Công Minh & Ngô Văn Công

CƠ CHẾ TÍNH TOÁN:
1. Mô hình LightGBM: Nạp TRỰC TIẾP từ bundle đã đóng gói 'iot_nids_bundle.joblib'
   (TUYỆT ĐỐI không thay thế mô hình đã nghiệm thu).
2. 4 Mô hình đối sánh (Logistic Regression, Decision Tree, Random Forest, XGBoost):
   Được huấn luyện trên tập Train với đúng 12 đặc trưng và tham số chuẩn.
3. Đánh giá tính toán xác suất predict_proba trên tập Test độc lập.
4. Xuất file kết quả định lượng: 'roc_auc_results.csv'
5. Vẽ biểu đồ đường cong ROC 300 DPI lưu tại: 'report_assets/fig15_roc_curves.png'
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import roc_curve, roc_auc_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
TRAIN_SET_CSV = os.path.join(BASE_DIR, "train_set.csv")
TEST_SET_CSV = os.path.join(BASE_DIR, "test_set.csv")
SAMPLE_TEST_CSV = os.path.join(BASE_DIR, "sample_test_data", "sample_test_flows_5000.csv")
ROC_CSV_OUT = os.path.join(BASE_DIR, "roc_auc_results.csv")
REPORT_ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
FIG15_PATH = os.path.join(REPORT_ASSETS_DIR, "fig15_roc_curves.png")


def compute_roc_curves(n_train_samples: int = 150000, n_test_samples: int = 50000):
    print("=" * 76)
    print("  TÍNH TOÁN ĐƯỜNG CONG ROC VÀ DIỆN TÍCH AUC THẬT CHO 5 MÔ HÌNH MACHINE LEARNING")
    print("=" * 76)

    # 1. Nạp bundle LightGBM
    assert os.path.exists(BUNDLE_PATH), f"Không tìm thấy bundle tại: {BUNDLE_PATH}"
    print(f"[*] Nạp mô hình LightGBM tối ưu từ: {BUNDLE_PATH} ...")
    bundle = joblib.load(BUNDLE_PATH)
    lgbm_model = bundle["model"]
    encoders = bundle["encoders"]
    scaler = bundle["scaler"]
    features = bundle["features"]
    numeric_cols = bundle["numeric_cols"]
    categorical_cols = bundle["categorical_cols"]
    print(f"[+] Đã nạp thành công LightGBM ({len(features)} đặc trưng)!")

    # 2. Chuẩn bị tập Train để huấn luyện 4 mô hình đối sánh
    print(f"\n[*] Đang nạp {n_train_samples:,} dòng từ train_set.csv để huấn luyện 4 mô hình đối chứng...")
    train_df = pd.read_csv(TRAIN_SET_CSV, nrows=n_train_samples, low_memory=False)

    y_train = (train_df["label"].astype(str).apply(lambda x: 0 if "benign" in x.lower() else 1)).values
    X_train_df = train_df[features].copy()

    for col in categorical_cols:
        le = encoders[col]
        classes_dict = {c: i for i, c in enumerate(le.classes_)}
        X_train_df[col] = X_train_df[col].astype(str).map(classes_dict).fillna(0).astype(int)

    for col in numeric_cols:
        X_train_df[col] = pd.to_numeric(X_train_df[col].replace("-", "0"), errors="coerce").fillna(0.0)

    X_train = X_train_df.values
    X_train_scaled = scaler.transform(X_train)

    # Huấn luyện 4 mô hình đối chứng
    print("  + Đang huấn luyện Logistic Regression...")
    lr_model = LogisticRegression(max_iter=500, random_state=42)
    lr_model.fit(X_train_scaled, y_train)

    print("  + Đang huấn luyện Decision Tree...")
    dt_model = DecisionTreeClassifier(max_depth=16, random_state=42)
    dt_model.fit(X_train, y_train)

    print("  + Đang huấn luyện Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=50, max_depth=14, n_jobs=-1, random_state=42)
    rf_model.fit(X_train, y_train)

    print("  + Đang huấn luyện XGBoost (Hist)...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=70, max_depth=6, learning_rate=0.1,
        eval_metric='logloss', random_state=42, n_jobs=-1, tree_method='hist'
    )
    xgb_model.fit(X_train, y_train)

    # 3. Chuẩn bị tập Test độc lập
    print(f"\n[*] Đang nạp {n_test_samples:,} dòng từ test_set.csv để kiểm thử tính toán ROC...")
    test_df = pd.read_csv(TEST_SET_CSV, nrows=n_test_samples, low_memory=False)
    y_test = (test_df["label"].astype(str).apply(lambda x: 0 if "benign" in x.lower() else 1)).values
    X_test_df = test_df[features].copy()

    for col in categorical_cols:
        le = encoders[col]
        classes_dict = {c: i for i, c in enumerate(le.classes_)}
        X_test_df[col] = X_test_df[col].astype(str).map(classes_dict).fillna(0).astype(int)

    for col in numeric_cols:
        X_test_df[col] = pd.to_numeric(X_test_df[col].replace("-", "0"), errors="coerce").fillna(0.0)

    X_test = X_test_df.values
    X_test_scaled = scaler.transform(X_test)

    # 4. Tính toán xác suất predict_proba và ROC/AUC
    models_dict = {
        "Logistic Regression": (lr_model, X_test_scaled, "#EF4444", "-."),
        "Decision Tree": (dt_model, X_test, "#F59E0B", "--"),
        "Random Forest": (rf_model, X_test, "#8B5CF6", ":"),
        "XGBoost": (xgb_model, X_test, "#06B6D4", "--"),
        "LightGBM (Đề xuất)": (lgbm_model, X_test_df, "#10B981", "-")
    }

    auc_records = []
    roc_plot_data = {}

    print("\n" + "=" * 65)
    print(f"{'MÔ HÌNH HỌC MÁY':<25} | {'ROC-AUC SCORE':<16} | {'SỐ MẪU TEST':<15}")
    print("=" * 65)

    for name, (clf, X_in, color, line_style) in models_dict.items():
        if name == "LightGBM (Đề xuất)":
            y_prob = clf.predict_proba(X_in)[:, 1]
        else:
            y_prob = clf.predict_proba(X_in)[:, 1]

        auc = roc_auc_score(y_test, y_prob)
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)

        auc_records.append({
            "Model": name,
            "ROC_AUC": round(auc, 6),
            "Test_Samples": len(y_test),
            "Malicious_Count": int(np.sum(y_test == 1)),
            "Benign_Count": int(np.sum(y_test == 0))
        })
        roc_plot_data[name] = (fpr, tpr, auc, color, line_style)

        print(f"{name:<25} | {auc:>14.6f} | {len(y_test):>12,}")

    print("=" * 65)

    # Lưu bảng kết quả AUC
    auc_df = pd.DataFrame(auc_records)
    auc_df.to_csv(ROC_CSV_OUT, index=False)
    print(f"[+] Đã lưu dữ liệu định lượng ROC-AUC tại: {ROC_CSV_OUT}")

    # 5. Vẽ biểu đồ chuẩn in ấn khoa học 300 DPI
    print(f"\n[*] Đang kết xuất biểu đồ đường cong ROC 300 DPI ra: {FIG15_PATH} ...")
    os.makedirs(REPORT_ASSETS_DIR, exist_ok=True)

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)

    for name, (fpr, tpr, auc, color, line_style) in roc_plot_data.items():
        lw = 2.4 if "LightGBM" in name else 1.8
        label_text = f"{name} (AUC = {auc:.4f})"
        ax.plot(fpr, tpr, color=color, linestyle=line_style, linewidth=lw, label=label_text)

    # Đường tham chiếu ngẫu nhiên (Random Guess)
    ax.plot([0, 1], [0, 1], color='#64748B', linestyle=':', linewidth=1.2, label='Phân loại ngẫu nhiên (AUC = 0.5000)')

    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.02])
    ax.set_xlabel('Tỷ lệ Báo động Giả - False Positive Rate (FPR)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Tỷ lệ Bắt đúng - True Positive Rate (TPR / Recall)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title('ĐƯỜNG CONG ROC VÀ CHỈ SỐ AUC ĐỐI SÁNH 5 MÔ HÌNH MACHINE LEARNING\n(Kiểm thử độc lập trên tập dữ liệu Stratosphere IoT-23)',
                 fontsize=13, fontweight='bold', pad=15, color='#0F172A')

    # Zoom in góc trái trên để thể hiện độ nhạy
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(FIG15_PATH, dpi=300)
    plt.close()
    print(f"[+] Xuất thành công biểu đồ ROC 300 DPI tại: {FIG15_PATH}")


if __name__ == "__main__":
    compute_roc_curves()

