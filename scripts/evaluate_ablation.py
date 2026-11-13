# -*- coding: utf-8 -*-
"""
Ablation Study Script for IoT Botnet NIDS Project
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng
Chứng minh mô hình học tổng thể hành vi luồng mạng thay vì phụ thuộc cục bộ vào một nhóm đặc trưng.
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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
TEST_SET_PATH = os.path.join(BASE_DIR, "test_set.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "ablation_study_results.csv")
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUTPUT_FIG = os.path.join(ASSETS_DIR, "figure_ablation_study.png")


def run_ablation_study():
    print("=" * 76)
    print("  MỤC 2: ABLATION STUDY - PHÂN TÍCH ĐỘ NHẠY ĐẶC TRƯNG CỦA MÔ HÌNH NIDS")
    print("=" * 76)

    assert os.path.exists(BUNDLE_PATH), f"Không tìm thấy bundle: {BUNDLE_PATH}"
    assert os.path.exists(TEST_SET_PATH), f"Không tìm thấy test set: {TEST_SET_PATH}"

    print(f"[*] Nạp mô hình đóng gói từ: {BUNDLE_PATH}")
    bundle = joblib.load(BUNDLE_PATH)
    model = bundle["model"]
    encoders = bundle["encoders"]
    scaler = bundle["scaler"]
    features = bundle["features"]
    numeric_cols = bundle["numeric_cols"]
    categorical_cols = bundle["categorical_cols"]

    print(f"[*] Nạp tập kiểm thử độc lập từ: {TEST_SET_PATH}...")
    t0 = time.time()
    # Nạp 200,000 dòng ngẫu nhiên hoặc toàn bộ tập test
    test_df = pd.read_csv(TEST_SET_PATH, low_memory=False)
    print(f"[+] Đã nạp {len(test_df):,} luồng kiểm thử trong {time.time() - t0:.2f}s.")

    # Chuẩn hóa nhãn thực tế
    target_col = 'label' if 'label' in test_df.columns else test_df.columns[-1]
    y_true = test_df[target_col].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1).values
    print(f"[*] Phân bố nhãn test: Benign={np.sum(y_true==0):,}, Malicious={np.sum(y_true==1):,}")

    # Tiền xử lý chuẩn baseline
    X_base = pd.DataFrame(index=test_df.index)
    for col in numeric_cols:
        X_base[col] = pd.to_numeric(test_df[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)

    for col in categorical_cols:
        le = encoders[col]
        classes_dict = {c: i for i, c in enumerate(le.classes_)}
        X_base[col] = test_df[col].astype(str).map(classes_dict).fillna(0).astype(int)

    X_base = X_base[features]

    # Định nghĩa các kịch bản Ablation
    ablation_scenarios = [
        ("Baseline (Full 12 Features)", []),
        ("Zero-out Numeric Group (9 cols)", numeric_cols),
        ("Zero-out Categorical Group (3 cols)", categorical_cols),
        ("Zero-out Top Feature (id.resp_p)", ['id.resp_p']),
        ("Zero-out Connection History (history)", ['history']),
        ("Zero-out Flow Volume (pkts & bytes)", ['orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes']),
        ("Zero-out Flow Duration (duration)", ['duration'])
    ]

    results = []
    baseline_f1 = None

    print("\n" + "=" * 90)
    print(f"{'KỊCH BẢN ABLATION':<38} | {'ACCURACY':<10} | {'PRECISION':<10} | {'RECALL':<10} | {'F1-SCORE':<10} | {'DELTA F1':<8}")
    print("=" * 90)

    for scenario_name, zero_cols in ablation_scenarios:
        X_ablated = X_base.copy()
        for col in zero_cols:
            X_ablated[col] = 0

        y_pred = model.predict(X_ablated.values)

        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        if baseline_f1 is None:
            baseline_f1 = f1
            delta_f1 = 0.0
        else:
            delta_f1 = f1 - baseline_f1

        results.append({
            "Scenario": scenario_name,
            "Zeroed_Features": ", ".join(zero_cols) if zero_cols else "None",
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1_Score": f1,
            "Delta_F1": delta_f1
        })

        delta_str = f"{delta_f1*100:+.2f}%" if delta_f1 != 0 else "0.00%"
        print(f"{scenario_name:<38} | {acc*100:>8.2f}% | {prec*100:>8.2f}% | {rec*100:>8.2f}% | {f1*100:>8.2f}% | {delta_str:>8}")

    print("=" * 90)

    res_df = pd.DataFrame(results)
    res_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] Đã lưu kết quả Ablation Study vào: {OUTPUT_CSV}")

    # Vẽ biểu đồ thanh Ablation Study
    os.makedirs(ASSETS_DIR, exist_ok=True)
    plt.figure(figsize=(10, 6), dpi=300)
    y_pos = np.arange(len(results))
    f1_values = [r["F1_Score"] * 100 for r in results]
    scenarios = [r["Scenario"] for r in results]

    colors = ['#1a73e8' if i == 0 else '#e53935' if f1_values[i] < 90 else '#fb8c00' for i in range(len(results))]
    bars = plt.barh(y_pos, f1_values, color=colors, height=0.6)

    plt.axvline(x=baseline_f1 * 100, color='#1a73e8', linestyle='--', alpha=0.7, label=f'Baseline F1 ({baseline_f1*100:.2f}%)')
    plt.xlim(0, 105)
    plt.yticks(y_pos, scenarios, fontsize=9)
    plt.xlabel('F1-Score (%)', fontsize=11, fontweight='bold')
    plt.title('Ablation Study: Tác động khi ẩn các nhóm đặc trưng lên hiệu năng F1-Score', fontsize=12, fontweight='bold', pad=15)
    plt.gca().invert_yaxis()

    for bar, r in zip(bars, results):
        w = bar.get_width()
        d_str = f" ({r['Delta_F1']*100:+.2f}%)" if r['Delta_F1'] != 0 else " (Base)"
        plt.text(w + 1, bar.get_y() + bar.get_height() / 2, f"{w:.2f}%{d_str}", va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_FIG)
    plt.close()
    print(f"[+] Đã xuất biểu đồ trực quan hóa vào: {OUTPUT_FIG}")

    return res_df


if __name__ == "__main__":
    run_ablation_study()
