# -*- coding: utf-8 -*-
"""
Out-of-Distribution (OOD) & PR-AUC Evaluation Script for IoT Botnet NIDS Project
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng

Kiểm thử khả năng khái quát hóa ngoài miền (Leave-One-Scenario-Out):
- Huấn luyện trên các kịch bản botnet phổ biến (Mirai, Hajime, Hakai, Muhstik, Benign).
- Kiểm thử ngoài miền trên kịch bản Botnet Torii hoàn toàn mới lạ chưa từng gặp (Capture 20-1 & 21-1).
- Tính toán đầy đủ: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, FNR.
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
TRAIN_SET_PATH = os.path.join(BASE_DIR, "train_set.csv")
TORII_20_PATH = os.path.join(BASE_DIR, "Capture-20-1_Torii.labeled")
TORII_21_PATH = os.path.join(BASE_DIR, "Capture-21-1_Torii.labeled")
OUTPUT_CSV = os.path.join(BASE_DIR, "ood_evaluation_results.csv")
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUTPUT_FIG = os.path.join(ASSETS_DIR, "figure_ood_pr_roc_curve.png")

ZEEK_COLUMNS = [
    'ts', 'uid', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p',
    'proto', 'service', 'duration', 'orig_bytes', 'resp_bytes',
    'conn_state', 'local_orig', 'local_resp', 'missed_bytes',
    'history', 'orig_pkts', 'orig_ip_bytes', 'resp_pkts',
    'resp_ip_bytes', 'tunnel_parents', 'label', 'detailed-label'
]

NUMERIC_FEATURES = [
    'id.orig_p', 'id.resp_p', 'duration', 'orig_bytes', 'resp_bytes',
    'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes'
]
CATEGORICAL_FEATURES = ['proto', 'conn_state', 'history']
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_zeek_labeled(file_path: str) -> pd.DataFrame:
    """Tải file conn.log.labeled định dạng Zeek."""
    return pd.read_csv(
        file_path,
        sep=r'\s+',
        comment='#',
        names=ZEEK_COLUMNS,
        low_memory=False
    )


def preprocess_df_with_bundle(df: pd.DataFrame, encoders, features) -> np.ndarray:
    """Tiền xử lý dữ liệu kiểm thử theo đúng bộ mã hóa của bundle."""
    X = pd.DataFrame(index=df.index)
    for col in NUMERIC_FEATURES:
        X[col] = pd.to_numeric(df[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        cdict = {c: i for i, c in enumerate(le.classes_)}
        X[col] = df[col].astype(str).map(cdict).fillna(0).astype(int)
    return X[features].values


def run_ood_evaluation():
    print("=" * 80)
    print("  MỤC 3: ĐÁNH GIÁ NGOÀI MIỀN (OUT-OF-DISTRIBUTION) & PR-AUC TRÊN BOTNET TORII")
    print("=" * 80)

    # 1. Nạp và gộp dữ liệu kiểm thử OOD Torii (Capture 20-1 và Capture 21-1)
    print(f"[*] Nạp kịch bản Torii Capture 20-1 từ: {TORII_20_PATH}...")
    df_torii_20 = load_zeek_labeled(TORII_20_PATH)
    df_torii_20['scenario'] = 'Capture-20-1_Torii'

    print(f"[*] Nạp kịch bản Torii Capture 21-1 từ: {TORII_21_PATH}...")
    df_torii_21 = load_zeek_labeled(TORII_21_PATH)
    df_torii_21['scenario'] = 'Capture-21-1_Torii'

    df_ood_combined = pd.concat([df_torii_20, df_torii_21], ignore_index=True)
    y_ood = df_ood_combined['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values
    total_ood = len(df_ood_combined)
    n_mal = int(np.sum(y_ood == 1))
    n_ben = int(np.sum(y_ood == 0))

    print(f"[+] Tổng tập kiểm thử OOD Torii: {total_ood:,} luồng mạng.")
    print(f"    - Độc hại (Torii C&C): {n_mal} luồng ({n_mal/total_ood*100:.2f}%)")
    print(f"    - Hợp lệ (Background Benign): {n_ben:,} luồng ({n_ben/total_ood*100:.2f}%)")

    # 2. Nạp Bundle triển khai hiện hành
    bundle = joblib.load(BUNDLE_PATH)
    deployed_model = bundle["model"]
    encoders = bundle["encoders"]
    features = bundle["features"]

    X_ood_mat = preprocess_df_with_bundle(df_ood_combined, encoders, features)

    # 3. Huấn luyện mô hình thuần OOD (Strict Leave-One-Scenario-Out)
    # Lọc bỏ 100% Torii khỏi dữ liệu huấn luyện
    print("\n[*] Nạp tập huấn luyện để lọc sạch 100% kịch bản Torii (Strict Leave-One-Scenario-Out)...")
    train_df = pd.read_csv(TRAIN_SET_PATH, low_memory=False)
    if 'scenario_tag' in train_df.columns:
        train_non_torii = train_df[~train_df['scenario_tag'].str.contains('Torii', case=False, na=False)].copy()
    else:
        train_non_torii = train_df.copy()

    print(f"[+] Dữ liệu huấn luyện Non-Torii: {len(train_non_torii):,} luồng (đã loại bỏ sạch Torii).")

    y_train_non_torii = train_non_torii['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values

    X_train_prep = pd.DataFrame(index=train_non_torii.index)
    for col in NUMERIC_FEATURES:
        X_train_prep[col] = pd.to_numeric(train_non_torii[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        cdict = {c: i for i, c in enumerate(le.classes_)}
        X_train_prep[col] = train_non_torii[col].astype(str).map(cdict).fillna(0).astype(int)

    X_train_mat = X_train_prep[features].values

    print("[*] Huấn luyện mô hình Strict OOD LightGBM (100 cây, chưa từng nhìn thấy Torii)...")
    strict_ood_model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    strict_ood_model.fit(X_train_mat, y_train_non_torii)
    print("[+] Huấn luyện mô hình Strict OOD LightGBM hoàn tất!")

    # 4. Đánh giá chi tiết trên 2 mô hình: (A) Deployed Bundle, (B) Strict OOD Model
    models_to_eval = [
        ("Deployed Bundle (LGBM - Trained with Stratified Split)", deployed_model),
        ("Strict OOD Model (LGBM - Zero Torii in Training Data)", strict_ood_model)
    ]

    results = []
    plot_data = []

    print("\n" + "=" * 96)
    print(f"{'MÔ HÌNH KIỂM THỬ OOD':<42} | {'ACC':<7} | {'PREC':<7} | {'REC':<7} | {'F1':<7} | {'ROC-AUC':<8} | {'PR-AUC':<8} | {'FPR':<7} | {'FNR':<7}")
    print("=" * 96)

    for m_name, mdl in models_to_eval:
        y_pred = mdl.predict(X_ood_mat)
        y_prob = mdl.predict_proba(X_ood_mat)[:, 1]

        acc = accuracy_score(y_ood, y_pred)
        prec = precision_score(y_ood, y_pred, zero_division=0)
        rec = recall_score(y_ood, y_pred, zero_division=0)
        f1 = f1_score(y_ood, y_pred, zero_division=0)

        cm = confusion_matrix(y_ood, y_pred)
        tn, fp, fn, tp = cm.ravel()

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        roc_auc = roc_auc_score(y_ood, y_prob)
        pr_auc = average_precision_score(y_ood, y_prob)

        fpr_curve, tpr_curve, _ = roc_curve(y_ood, y_prob)
        p_curve, r_curve, _ = precision_recall_curve(y_ood, y_prob)
        plot_data.append((m_name, fpr_curve, tpr_curve, roc_auc, p_curve, r_curve, pr_auc))

        results.append({
            "Model_Name": m_name,
            "Test_Scenario": "OOD_Torii_Combined (Capture-20 & Capture-21)",
            "Total_Samples": total_ood,
            "Malicious_Count": n_mal,
            "Benign_Count": n_ben,
            "TP": tp,
            "TN": tn,
            "FP": fp,
            "FN": fn,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1_Score": f1,
            "ROC_AUC": roc_auc,
            "PR_AUC": pr_auc,
            "FPR": fpr,
            "FNR": fnr
        })

        print(f"{m_name:<42} | {acc*100:>5.2f}% | {prec*100:>5.2f}% | {rec*100:>5.2f}% | {f1*100:>5.2f}% | {roc_auc:>8.4f} | {pr_auc:>8.4f} | {fpr*100:>5.2f}% | {fnr*100:>5.2f}%")

    print("=" * 96)

    # 5. Đánh giá riêng lẻ từng capture Torii
    print("\n[+] ĐÁNH GIÁ OOD CHI TIẾT TRÊN TỪNG CAPTURE TORII:")
    for cap_name, sub_df in [("Capture-20-1_Torii", df_torii_20), ("Capture-21-1_Torii", df_torii_21)]:
        y_sub = sub_df['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values
        X_sub = preprocess_df_with_bundle(sub_df, encoders, features)
        y_sub_pred = strict_ood_model.predict(X_sub)
        y_sub_prob = strict_ood_model.predict_proba(X_sub)[:, 1]

        sub_cm = confusion_matrix(y_sub, y_sub_pred)
        s_tn, s_fp, s_fn, s_tp = sub_cm.ravel()
        sub_rec = recall_score(y_sub, y_sub_pred, zero_division=0)
        sub_prec = precision_score(y_sub, y_sub_pred, zero_division=0)
        sub_pr_auc = average_precision_score(y_sub, y_sub_prob)

        print(f"  * {cap_name:<20}: TP={s_tp}/{s_tp+s_fn} (Recall: {sub_rec*100:.2f}%), FP={s_fp}, PR-AUC={sub_pr_auc:.4f}")

    # Xuất file CSV kết quả
    res_df = pd.DataFrame(results)
    res_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] ĐÃ LƯU TOÀN BỘ KẾT QUẢ ĐÁNH GIÁ OOD & PR-AUC VÀO: {OUTPUT_CSV}")

    # 6. Vẽ biểu đồ so sánh ROC Curve và PR Curve side-by-side
    os.makedirs(ASSETS_DIR, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # Subplot 1: ROC Curve
    for m_name, fpr_c, tpr_c, r_auc, _, _, _ in plot_data:
        label_text = f"{m_name[:24]}... (AUC = {r_auc:.4f})"
        ax1.plot(fpr_c, tpr_c, lw=2, label=label_text)
    ax1.plot([0, 1], [0, 1], color='navy', lw=1.5, linestyle='--', label='Random Guess (AUC = 0.5000)')
    ax1.set_xlim([0.0, 1.0])
    ax1.set_ylim([0.0, 1.05])
    ax1.set_xlabel('False Positive Rate (FPR)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('True Positive Rate (TPR / Recall)', fontsize=11, fontweight='bold')
    ax1.set_title('Receiver Operating Characteristic (ROC Curve) - OOD Torii', fontsize=11, fontweight='bold')
    ax1.legend(loc="lower right", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Subplot 2: Precision-Recall Curve
    no_skill = n_mal / total_ood
    ax2.plot([0, 1], [no_skill, no_skill], linestyle='--', color='navy', lw=1.5, label=f'Baseline Rate ({no_skill*100:.2f}%)')
    for m_name, _, _, _, p_c, r_c, pr_auc_val in plot_data:
        label_text = f"{m_name[:24]}... (PR-AUC = {pr_auc_val:.4f})"
        ax2.plot(r_c, p_c, lw=2, label=label_text)
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel('Recall', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Precision', fontsize=11, fontweight='bold')
    ax2.set_title('Precision-Recall Curve (PR-AUC) - OOD Torii (Imbalanced 99.5:0.5)', fontsize=11, fontweight='bold')
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_FIG)
    plt.close()
    print(f"[+] Đã xuất biểu đồ so sánh ROC & PR-AUC vào: {OUTPUT_FIG}")

    return res_df


if __name__ == "__main__":
    run_ood_evaluation()
