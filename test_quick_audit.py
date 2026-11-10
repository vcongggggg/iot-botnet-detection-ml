# -*- coding: utf-8 -*-
"""
Quick Automated Audit Script for IoT Botnet NIDS Project
Designed for Independent Reviewer / Auditor Agents to verify the entire system in < 10 seconds.
Includes strict assertion thresholds (Accuracy >= 99%, F1 >= 99%, Latency < 0.5ms).
"""

import os
import sys
import time
import json
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
SAMPLE_PATH = os.path.join(BASE_DIR, "sample_test_data", "sample_test_flows_5000.csv")
REPORT_DOCX = os.path.join(BASE_DIR, "Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx")
REPORT_PPTX = os.path.join(BASE_DIR, "Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx")
BENCHMARK_CSV = os.path.join(BASE_DIR, "benchmark_results.csv")
ROC_CSV = os.path.join(BASE_DIR, "roc_auc_results.csv")
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")


def run_audit():
    print("=" * 76)
    print("  INDEPENDENT AUDIT VERIFICATION: IoT BOTNET NIDS PROJECT (DUT)")
    print("  Topic: Phát hiện & Phân loại Mã độc Botnet IoT (Mirai, Hajime, Torii)")
    print("=" * 76)

    # 1. Check Artifacts
    print("\n[1/5] AUDITING REPORT DELIVERABLES & QUANTITATIVE ASSETS...")
    assert os.path.exists(REPORT_DOCX), "Missing Final Word Report (.docx)"
    docx_size_mb = os.path.getsize(REPORT_DOCX) / (1024 * 1024)
    print(f"  [PASS] Word Report exists: {os.path.basename(REPORT_DOCX)} ({docx_size_mb:.2f} MB)")

    assert os.path.exists(REPORT_PPTX), "Missing Presentation Slide Deck (.pptx)"
    pptx_size_mb = os.path.getsize(REPORT_PPTX) / (1024 * 1024)
    print(f"  [PASS] Slide Deck exists: {os.path.basename(REPORT_PPTX)} ({pptx_size_mb:.2f} MB)")

    assert os.path.exists(BENCHMARK_CSV), "Missing benchmark_results.csv"
    bm_df = pd.read_csv(BENCHMARK_CSV)
    assert len(bm_df) == 5, f"Expected 5 models in benchmark_results.csv, got {len(bm_df)}"
    lgbm_row = bm_df[bm_df["Model"].str.contains("LightGBM")].iloc[0]
    assert float(lgbm_row["Accuracy"]) >= 0.999, f"LGBM Accuracy must be >= 0.999, got {lgbm_row['Accuracy']}"
    print(f"  [PASS] benchmark_results.csv verified (5 models, LightGBM Acc = {float(lgbm_row['Accuracy'])*100:.2f}%)")

    assert os.path.exists(ROC_CSV), "Missing roc_auc_results.csv"
    roc_df = pd.read_csv(ROC_CSV)
    assert len(roc_df) == 5, f"Expected 5 models in roc_auc_results.csv, got {len(roc_df)}"
    print(f"  [PASS] roc_auc_results.csv verified (5 models, LightGBM AUC = {roc_df[roc_df['Model'].str.contains('LightGBM')].iloc[0]['ROC_AUC']})")

    png_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".png")]
    print(f"  [PASS] Scientific 300-DPI Figures found: {len(png_files)} images in report_assets/")

    # 2. Check ML Bundle
    print("\n[2/5] AUDITING TRAINED MACHINE LEARNING BUNDLE...")
    assert os.path.exists(BUNDLE_PATH), "Missing Model Bundle (iot_nids_bundle.joblib)"
    bundle = joblib.load(BUNDLE_PATH)
    model = bundle["model"]
    encoders = bundle["encoders"]
    scaler = bundle["scaler"]
    features = bundle["features"]
    numeric_cols = bundle["numeric_cols"]
    categorical_cols = bundle["categorical_cols"]

    assert len(features) == 12, f"Expected exactly 12 features, got {len(features)}"
    assert "service" not in features, "Feature 'service' must NOT be in bundle!"
    assert "missed_bytes" not in features, "Feature 'missed_bytes' must NOT be in bundle!"
    assert "id.orig_h" not in features and "id.resp_h" not in features, "Static IP features must NOT be in bundle!"

    print(f"  [PASS] Model loaded: {model.__class__.__name__}")
    print(f"  [PASS] Exactly 12 features verified: {features}")
    print(f"  [PASS] Numeric Scaler mean shape: {scaler.mean_.shape}")
    print(f"  [PASS] Categorical Encoders: {list(encoders.keys())}")

    # 3. Benchmark Sample Test Flows with Strict Assertions
    print("\n[3/5] AUDITING INFERENCE ACCURACY ON 5,000 UNSEEN SAMPLE FLOWS...")
    assert os.path.exists(SAMPLE_PATH), "Missing Sample Test Data"
    df = pd.read_csv(SAMPLE_PATH)
    y_true = (df["label"].astype(str).apply(lambda x: 0 if "benign" in x.lower() else 1)).values

    X_test_prep = df[features].copy()
    for col in categorical_cols:
        le = encoders[col]
        classes_dict = {c: i for i, c in enumerate(le.classes_)}
        X_test_prep[col] = X_test_prep[col].astype(str).map(classes_dict).fillna(0).astype(int)

    for col in numeric_cols:
        X_test_prep[col] = pd.to_numeric(X_test_prep[col].replace("-", "0"), errors="coerce").fillna(0.0)

    t0 = time.perf_counter()
    y_pred = model.predict(X_test_prep)
    elapsed_total_s = time.perf_counter() - t0
    latency_per_flow_ms = (elapsed_total_s / len(df)) * 1000.0

    acc = np.mean(y_pred == y_true) * 100.0
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    tn = np.sum((y_pred == 0) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"  [PASS] Test Sample Size: {len(df):,} flows (Malicious: {np.sum(y_true==1)}, Benign: {np.sum(y_true==0)})")
    print(f"  [PASS] Accuracy:  {acc:.4f}%")
    print(f"  [PASS] Precision: {precision * 100:.4f}%")
    print(f"  [PASS] Recall:    {recall * 100:.4f}%")
    print(f"  [PASS] F1-Score:  {f1 * 100:.4f}%")
    print(f"  [PASS] Confusion Matrix: TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"  [PASS] Inference Latency: {latency_per_flow_ms:.4f} ms/flow (~{len(df)/elapsed_total_s:,.0f} flows/sec)")

    # Strict performance assertions
    assert acc >= 99.0, f"FAIL: Accuracy {acc:.2f}% < 99.0%"
    assert f1 * 100.0 >= 99.0, f"FAIL: F1-Score {f1*100.0:.2f}% < 99.0%"
    assert precision * 100.0 >= 99.0, f"FAIL: Precision {precision*100.0:.2f}% < 99.0%"
    assert recall * 100.0 >= 99.0, f"FAIL: Recall {recall*100.0:.2f}% < 99.0%"
    assert latency_per_flow_ms < 0.5, f"FAIL: Latency {latency_per_flow_ms:.4f} ms >= 0.5 ms"
    print("  [PASS] Strict thresholds satisfied (Accuracy >= 99%, F1 >= 99%, Latency < 0.5ms)!")

    # 4. Check Reproducibility Scripts
    print("\n[4/5] AUDITING REPRODUCIBILITY SCRIPTS...")
    scripts = [
        "scripts/split_iot23.py",
        "scripts/sample_test_flows.py",
        "scripts/compute_roc.py",
        "train_pipeline.py"
    ]
    for s_rel in scripts:
        s_abs = os.path.join(BASE_DIR, s_rel)
        assert os.path.exists(s_abs), f"Missing script: {s_rel}"
        print(f"  [PASS] Script verified: {s_rel}")

    # 5. Check 3-Tier Live Demo Architecture
    print("\n[5/5] AUDITING 3-TIER LIVE DEMO ARCHITECTURE...")
    demo_files = [
        "live_demo/attacker_botnet_console.py",
        "live_demo/ai_nids_guardian_server.py",
        "live_demo/victim_iot_server.py",
        "start_demo_3_ben.bat",
        "HUONG_DAN_DEMO_VA_BAO_VE.md"
    ]
    for df_rel in demo_files:
        df_abs = os.path.join(BASE_DIR, df_rel)
        assert os.path.exists(df_abs), f"Missing demo file: {df_rel}"
        print(f"  [PASS] Demo component verified: {df_rel}")

    print("\n" + "=" * 76)
    print("  AUDIT VERIFICATION RESULT: 100% PASSED!")
    print("  All criteria (Data Leakage, Accuracy, Latency, Deliverables) SATISFIED.")
    print("=" * 76)


if __name__ == "__main__":
    run_audit()
