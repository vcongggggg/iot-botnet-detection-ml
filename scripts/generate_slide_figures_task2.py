# -*- coding: utf-8 -*-
"""
Generate Publication & Slide Figures (300 DPI) for IoT NIDS Presentation
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng
Xuất các biểu đồ đẹp mắt, nền trắng, độ phân giải cao phục vụ bộ slide thuyết trình.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
SLIDE_FIG_DIR = os.path.join(BASE_DIR, "figures_slide")
os.makedirs(SLIDE_FIG_DIR, exist_ok=True)

# 1. Vẽ figures_slide/per_family_recall.png
def plot_per_family_recall():
    csv_path = os.path.join(BASE_DIR, "multiclass_evaluation_results.csv")
    out_fig = os.path.join(SLIDE_FIG_DIR, "per_family_recall.png")
    assert os.path.exists(csv_path), f"Không tìm thấy: {csv_path}"

    df = pd.read_csv(csv_path)
    sub = df[df["Evaluation_Type"] == "Binary_Model_Per_Family_Recall"].copy()

    classes = sub["Class_or_Family"].tolist()
    recalls = [r * 100.0 for r in sub["Recall"]]
    samples = sub["Total_Samples"].tolist()

    plt.figure(figsize=(10, 5.5), dpi=300)
    plt.style.use('default')
    ax = plt.gca()
    ax.set_facecolor('white')
    plt.grid(axis='x', linestyle='--', alpha=0.3, color='#94a3b8')

    colors = ['#10b981' if r >= 99.0 else '#f59e0b' if r >= 50.0 else '#ef4444' for r in recalls]
    y_pos = np.arange(len(classes))
    bars = plt.barh(y_pos, recalls, color=colors, height=0.55, edgecolor='none')

    plt.yticks(y_pos, classes, fontsize=11, fontweight='bold', color='#1e293b')
    plt.xlabel('Tỷ lệ Phát hiện / Recall (%)', fontsize=12, fontweight='bold', color='#0f172a', labelpad=10)
    plt.xlim(0, 115)
    plt.title('TỶ LỆ PHÁT HIỆN THEO TỪNG HỌ MÃ ĐỘC & DẠNG TẤN CÔNG (1.14M LUỒNG TEST)\n(Mô hình LightGBM hiện hành phát hiện hoàn hảo PortScan/DDoS nhưng bỏ sót Torii C&C)',
              fontsize=12, fontweight='bold', color='#0f172a', pad=15)
    plt.gca().invert_yaxis()

    for bar, r, s in zip(bars, recalls, samples):
        w = bar.get_width()
        txt = f"{r:.2f}% (N={s:,})" if r > 0 else f"0.00% (Bị bỏ sót! N={s})"
        plt.text(w + 1.5, bar.get_y() + bar.get_height() / 2, txt,
                 va='center', fontsize=10, fontweight='bold',
                 color='#ef4444' if r == 0 else '#0f172a')

    plt.tight_layout()
    plt.savefig(out_fig, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f"[+] Đã xuất slide figure: {out_fig}")


# 2. Vẽ figures_slide/ablation.png
def plot_ablation_study():
    csv_path = os.path.join(BASE_DIR, "ablation_study_results.csv")
    out_fig = os.path.join(SLIDE_FIG_DIR, "ablation.png")
    assert os.path.exists(csv_path), f"Không tìm thấy: {csv_path}"

    df = pd.read_csv(csv_path)
    scenarios = df["Scenario"].tolist()
    f1_scores = [f * 100.0 for f in df["F1_Score"]]
    deltas = df["Delta_F1"].tolist()

    plt.figure(figsize=(10, 5.5), dpi=300)
    plt.style.use('default')
    ax = plt.gca()
    ax.set_facecolor('white')
    plt.grid(axis='x', linestyle='--', alpha=0.3, color='#94a3b8')

    colors = ['#2563eb' if i == 0 else '#10b981' if f >= 90.0 else '#ef4444' for i, f in enumerate(f1_scores)]
    y_pos = np.arange(len(scenarios))
    bars = plt.barh(y_pos, f1_scores, color=colors, height=0.55)

    plt.yticks(y_pos, scenarios, fontsize=10, fontweight='bold', color='#1e293b')
    plt.xlabel('F1-Score (%)', fontsize=12, fontweight='bold', color='#0f172a', labelpad=10)
    plt.xlim(0, 115)
    plt.title('ABLATION STUDY: TÁC ĐỘNG KHI ẨN CÁC NHÓM ĐẶC TRƯNG LÊN F1-SCORE\n(Chứng minh mô hình phụ thuộc chặt chẽ vào tương quan Cổng Đích & Lịch sử TCP)',
              fontsize=12, fontweight='bold', color='#0f172a', pad=15)
    plt.gca().invert_yaxis()

    for bar, f, d in zip(bars, f1_scores, deltas):
        w = bar.get_width()
        d_str = f" ({d*100:+.2f}%)" if d != 0 else " (Chuẩn)"
        plt.text(w + 1.5, bar.get_y() + bar.get_height() / 2, f"{f:.2f}%{d_str}",
                 va='center', fontsize=9.5, fontweight='bold', color='#0f172a')

    plt.tight_layout()
    plt.savefig(out_fig, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f"[+] Đã xuất slide figure: {out_fig}")


# 3. Vẽ figures_slide/ood_results.png
def plot_ood_results():
    from scripts.evaluate_ood import (
        load_zeek_labeled, preprocess_df_with_bundle,
        TORII_20_PATH, TORII_21_PATH, BUNDLE_PATH, TRAIN_SET_PATH,
        NUMERIC_FEATURES, CATEGORICAL_FEATURES
    )
    from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score, average_precision_score
    import lightgbm as lgb

    out_fig = os.path.join(SLIDE_FIG_DIR, "ood_results.png")

    df_torii_20 = load_zeek_labeled(TORII_20_PATH)
    df_torii_21 = load_zeek_labeled(TORII_21_PATH)
    df_ood = pd.concat([df_torii_20, df_torii_21], ignore_index=True)
    y_ood = df_ood['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values

    bundle = pd.read_pickle(BUNDLE_PATH) if BUNDLE_PATH.endswith('.pkl') else joblib.load(BUNDLE_PATH)
    deployed_model = bundle["model"]
    encoders = bundle["encoders"]
    features = bundle["features"]

    X_ood = preprocess_df_with_bundle(df_ood, encoders, features)

    # Train Strict OOD Model
    train_df = pd.read_csv(TRAIN_SET_PATH, low_memory=False)
    train_non_torii = train_df[~train_df['scenario_tag'].str.contains('Torii', case=False, na=False)].copy()
    y_train_non = train_non_torii['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values

    X_train_prep = pd.DataFrame(index=train_non_torii.index)
    for col in NUMERIC_FEATURES:
        X_train_prep[col] = pd.to_numeric(train_non_torii[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        cdict = {c: i for i, c in enumerate(le.classes_)}
        X_train_prep[col] = train_non_torii[col].astype(str).map(cdict).fillna(0).astype(int)

    strict_ood_model = lgb.LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1)
    strict_ood_model.fit(X_train_prep[features].values, y_train_non)

    # Curves
    prob_dep = deployed_model.predict_proba(X_ood)[:, 1]
    prob_ood = strict_ood_model.predict_proba(X_ood)[:, 1]

    fpr_dep, tpr_dep, _ = roc_curve(y_ood, prob_dep)
    fpr_ood, tpr_ood, _ = roc_curve(y_ood, prob_ood)
    auc_dep = roc_auc_score(y_ood, prob_dep)
    auc_ood = roc_auc_score(y_ood, prob_ood)

    p_dep, r_dep, _ = precision_recall_curve(y_ood, prob_dep)
    p_ood, r_ood, _ = precision_recall_curve(y_ood, prob_ood)
    pr_dep = average_precision_score(y_ood, prob_dep)
    pr_ood = average_precision_score(y_ood, prob_ood)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    fig.patch.set_facecolor('white')

    # Subplot 1: ROC Curve
    ax1.set_facecolor('white')
    ax1.plot(fpr_dep, tpr_dep, color='#2563eb', lw=2.5, label=f'Model Trong Miền (ROC-AUC = {auc_dep:.4f})')
    ax1.plot(fpr_ood, tpr_ood, color='#dc2626', lw=2.5, linestyle='--', label=f'Model Ngoài Miền OOD (ROC-AUC = {auc_ood:.4f})')
    ax1.plot([0, 1], [0, 1], color='#94a3b8', linestyle=':', lw=1.2, label='Đoán ngẫu nhiên (AUC = 0.5000)')
    ax1.set_xlim([-0.02, 1.02])
    ax1.set_ylim([-0.02, 1.05])
    ax1.set_xlabel('False Positive Rate (FPR)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('True Positive Rate (Recall)', fontsize=11, fontweight='bold')
    ax1.set_title('(A) ROC Curve: ROC-AUC vẫn cao giả tạo (~0.97)', fontsize=12, fontweight='bold', pad=12)
    ax1.legend(loc="lower right", fontsize=9.5, frameon=True)
    ax1.grid(True, linestyle='--', alpha=0.3)

    # Subplot 2: PR Curve
    ax2.set_facecolor('white')
    no_skill = np.sum(y_ood == 1) / len(y_ood)
    ax2.plot([0, 1], [no_skill, no_skill], linestyle=':', color='#94a3b8', lw=1.2, label=f'Ngưỡng cơ sở (0.46%)')
    ax2.plot(r_dep, p_dep, color='#2563eb', lw=2.5, label=f'Model Trong Miền (PR-AUC = {pr_dep:.4f})')
    ax2.plot(r_ood, p_ood, color='#dc2626', lw=2.5, linestyle='--', label=f'Model Ngoài Miền OOD (PR-AUC = {pr_ood:.4f})')
    ax2.set_xlim([-0.02, 1.02])
    ax2.set_ylim([-0.02, 1.05])
    ax2.set_xlabel('Recall (Tỷ lệ bắt trúng Torii)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Precision (Độ chuẩn xác)', fontsize=11, fontweight='bold')
    ax2.set_title('(B) PR-AUC Curve: Phản ánh trung thực suy giảm khi gặp Torii', fontsize=12, fontweight='bold', pad=12)
    ax2.legend(loc="upper right", fontsize=9.5, frameon=True)
    ax2.grid(True, linestyle='--', alpha=0.3)

    plt.suptitle('ĐỐI SÁNH HIỆU NĂNG NGOÀI MIỀN (OOD) TRÊN BOTNET TORII: ROC-AUC vs PR-AUC',
                 fontsize=13, fontweight='bold', y=0.98, color='#0f172a')
    plt.tight_layout()
    plt.savefig(out_fig, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close()
    print(f"[+] Đã xuất slide figure: {out_fig}")


if __name__ == "__main__":
    print("[*] Đang tạo các biểu đồ phục vụ Slide...")
    plot_per_family_recall()
    plot_ablation_study()
    plot_ood_results()
    print("[+] Hoàn thành sinh 3 biểu đồ slide từ Task 2!")
