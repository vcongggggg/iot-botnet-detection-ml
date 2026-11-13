# -*- coding: utf-8 -*-
"""
Multiclass & Per-Family Evaluation Script for IoT Botnet NIDS Project
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng
Báo cáo chi tiết Precision, Recall, F1 theo từng họ mã độc và từng dạng hành vi tấn công (Torii, C&C, Mirai, DDoS, PortScan).
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
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
TRAIN_SET_PATH = os.path.join(BASE_DIR, "train_set.csv")
TEST_SET_PATH = os.path.join(BASE_DIR, "test_set.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "multiclass_evaluation_results.csv")
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUTPUT_CM_FIG = os.path.join(ASSETS_DIR, "figure_multiclass_confusion_matrix.png")

NUMERIC_FEATURES = [
    'id.orig_p', 'id.resp_p', 'duration', 'orig_bytes', 'resp_bytes',
    'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes'
]
CATEGORICAL_FEATURES = ['proto', 'conn_state', 'history']
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def vectorize_attack_classes(df: pd.DataFrame) -> pd.Series:
    """Vectorized categorization into 6 major behavior classes."""
    lbl = df['label'].astype(str).str.lower()
    det = df['detailed-label'].astype(str) if 'detailed-label' in df.columns else pd.Series('', index=df.index)
    tag = df['scenario_tag'].astype(str) if 'scenario_tag' in df.columns else pd.Series('', index=df.index)

    is_benign = lbl.str.contains('benign') | (det == '-')
    is_torii = (~is_benign) & (tag.str.contains('Torii', case=False) | det.str.contains('Torii', case=False))
    is_cnc = (~is_benign) & (~is_torii) & (det.str.contains('C&C', case=False) | tag.str.contains('C&C', case=False))
    is_ddos = (~is_benign) & (~is_torii) & (~is_cnc) & det.str.contains('DDoS', case=False)
    is_portscan = (~is_benign) & (~is_torii) & (~is_cnc) & (~is_ddos) & det.str.contains('PortScan', case=False)
    is_attack = (~is_benign) & (~is_torii) & (~is_cnc) & (~is_ddos) & (~is_portscan) & det.str.contains('Attack', case=False)

    conditions = [is_benign, is_torii, is_cnc, is_ddos, is_portscan, is_attack]
    choices = ['Benign', 'Torii (C&C)', 'C&C (Generic)', 'DDoS', 'PortScan', 'Attack/BruteForce']
    return pd.Series(np.select(conditions, choices, default='Other_Malicious'), index=df.index)


def run_multiclass_evaluation():
    print("=" * 80)
    print("  MỤC 1: ĐÁNH GIÁ PHÂN LOẠI ĐA LỚP & RECALL CHI TIẾT THEO TỪNG HỌ MÃ ĐỘC")
    print("=" * 80)

    # 1. Đánh giá khả năng phát hiện của Deployed Binary Model trên từng lớp chi tiết
    print("\n[BƯỚC 1/2] ĐÁNH GIÁ TẬP TEST (1.14M LUỒNG) BẰNG BUNDLE HIỆN HÀNH (RECALL THEO HỌ)")
    bundle = joblib.load(BUNDLE_PATH)
    binary_model = bundle["model"]
    encoders = bundle["encoders"]
    features = bundle["features"]

    print(f"[*] Nạp tập kiểm thử từ: {TEST_SET_PATH}...")
    t0 = time.time()
    test_df = pd.read_csv(TEST_SET_PATH, low_memory=False)
    print(f"[+] Đã nạp {len(test_df):,} luồng test trong {time.time() - t0:.2f}s.")

    test_df['attack_class'] = vectorize_attack_classes(test_df)

    # Tiền xử lý tập test
    X_test_prep = pd.DataFrame(index=test_df.index)
    for col in NUMERIC_FEATURES:
        X_test_prep[col] = pd.to_numeric(test_df[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        cdict = {c: i for i, c in enumerate(le.classes_)}
        X_test_prep[col] = test_df[col].astype(str).map(cdict).fillna(0).astype(int)

    X_test_mat = X_test_prep[features].values
    y_test_pred = binary_model.predict(X_test_mat)
    test_df['pred_binary'] = y_test_pred

    binary_recall_rows = []
    print("\n" + "-" * 76)
    print(f"{'HỌ MÃ ĐỘC / HÀNH VI TẤN CÔNG':<28} | {'TỔNG MẪU':<10} | {'ĐOÁN ĐÚNG':<10} | {'TỶ LỆ PHÁT HIỆN / RECALL':<20}")
    print("-" * 76)

    for cls_name in ['Benign', 'PortScan', 'DDoS', 'C&C (Generic)', 'Attack/BruteForce', 'Torii (C&C)']:
        sub = test_df[test_df['attack_class'] == cls_name]
        total = len(sub)
        if total == 0:
            continue
        if cls_name == 'Benign':
            correct = int(np.sum(sub['pred_binary'] == 0))
            metric_name = "True Negative Rate"
        else:
            correct = int(np.sum(sub['pred_binary'] == 1))
            metric_name = "Recall (Detection Rate)"
        rate = (correct / total) * 100.0 if total > 0 else 0.0

        binary_recall_rows.append({
            "Evaluation_Type": "Binary_Model_Per_Family_Recall",
            "Class_or_Family": cls_name,
            "Total_Samples": total,
            "Correct_Predictions": correct,
            "Precision": 1.0 if cls_name != 'Benign' and correct > 0 else (correct/total if cls_name == 'Benign' else 0.0),
            "Recall": correct / total if total > 0 else 0.0,
            "F1_Score": 2 * (correct/total) / (1 + (correct/total)) if (1 + (correct/total)) > 0 else 0.0,
            "Metric_Note": f"{metric_name}: {rate:.2f}%"
        })
        print(f"{cls_name:<28} | {total:>10,} | {correct:>10,} | {rate:>18.2f}% ({metric_name})")

    print("-" * 76)

    # Đánh giá theo kịch bản botnet (Scenario Tag)
    print("\n[+] ĐÁNH GIÁ THEO KỊCH BẢN THỰC THI (SCENARIO TAG):")
    for tag_name, grp in test_df.groupby('scenario_tag'):
        is_mal = grp['label'].astype(str).str.lower().str.contains('malicious')
        total_mal = int(np.sum(is_mal))
        if total_mal > 0:
            correct_mal = int(np.sum(is_mal & (grp['pred_binary'] == 1)))
            r_mal = correct_mal / total_mal * 100.0
            print(f"  - {tag_name:<20}: Phát hiện độc hại {correct_mal:>8,} / {total_mal:>8,} ({r_mal:>6.2f}%)")
            binary_recall_rows.append({
                "Evaluation_Type": "Binary_Model_Per_Scenario_Recall",
                "Class_or_Family": tag_name,
                "Total_Samples": total_mal,
                "Correct_Predictions": correct_mal,
                "Precision": 1.0 if correct_mal > 0 else 0.0,
                "Recall": correct_mal / total_mal,
                "F1_Score": correct_mal / total_mal,
                "Metric_Note": f"Scenario Malicious Recall: {r_mal:.2f}%"
            })
        else:
            correct_ben = int(np.sum(grp['pred_binary'] == 0))
            r_ben = correct_ben / len(grp) * 100.0
            print(f"  - {tag_name:<20}: Nhận diện lưu lượng sạch {correct_ben:>8,} / {len(grp):>8,} ({r_ben:>6.2f}%)")

    # 2. Huấn luyện Mô hình Đa lớp Chuyên biệt (Multiclass LightGBM Classifier)
    print("\n[BƯỚC 2/2] HUẤN LUYỆN & KIỂM ĐỊNH MÔ HÌNH ĐA LỚP MULTICLASS LIGHTGBM (6 LỚP HÀNH VI)")
    print(f"[*] Đang nạp dữ liệu huấn luyện từ: {TRAIN_SET_PATH}...")
    t1 = time.time()
    train_df = pd.read_csv(TRAIN_SET_PATH, low_memory=False)
    print(f"[+] Đã nạp {len(train_df):,} luồng huấn luyện trong {time.time() - t1:.2f}s.")

    train_df['attack_class'] = vectorize_attack_classes(train_df)

    # Encode multiclass target
    target_encoder = LabelEncoder()
    target_encoder.fit(['Benign', 'PortScan', 'DDoS', 'C&C (Generic)', 'Attack/BruteForce', 'Torii (C&C)'])
    class_labels = list(target_encoder.classes_)

    y_train_multi = target_encoder.transform(train_df['attack_class'])
    y_test_multi = target_encoder.transform(test_df['attack_class'])

    # Tiền xử lý X_train
    X_train_prep = pd.DataFrame(index=train_df.index)
    for col in NUMERIC_FEATURES:
        X_train_prep[col] = pd.to_numeric(train_df[col].replace('-', 0).replace('(empty)', 0), errors='coerce').fillna(0.0).astype(np.float32)
    for col in CATEGORICAL_FEATURES:
        le = encoders[col]
        cdict = {c: i for i, c in enumerate(le.classes_)}
        X_train_prep[col] = train_df[col].astype(str).map(cdict).fillna(0).astype(int)

    X_train_mat = X_train_prep[features].values

    # Lấy mẫu cân bằng phân tầng để huấn luyện nhanh và đảm bảo nhận diện lớp hiếm (Torii, Attack)
    print("[*] Tinh chỉnh trọng số mẫu (Class Weights) để khắc phục mất cân bằng lớp cực đoan...")
    class_counts = pd.Series(y_train_multi).value_counts().to_dict()
    total_samples = len(y_train_multi)
    n_classes = len(class_labels)
    class_weights = {cls: total_samples / (n_classes * count) for cls, count in class_counts.items()}
    sample_weight = np.array([class_weights[y] for y in y_train_multi])

    # Huấn luyện Multiclass LightGBM
    multi_lgbm = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=n_classes,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    print(f"[*] Bắt đầu huấn luyện Multiclass LightGBM trên {len(train_df):,} luồng...")
    t_train_start = time.time()
    multi_lgbm.fit(X_train_mat, y_train_multi, sample_weight=sample_weight)
    train_duration = time.time() - t_train_start
    print(f"[+] Huấn luyện Multiclass LightGBM hoàn tất trong {train_duration:.2f}s.")

    # Đánh giá trên toàn bộ tập test
    print(f"[*] Đánh giá Multiclass trên toàn bộ tập test ({len(test_df):,} luồng)...")
    t_eval_start = time.time()
    y_pred_multi = multi_lgbm.predict(X_test_mat)
    eval_duration = time.time() - t_eval_start
    print(f"[+] Suy luận Multiclass hoàn tất trong {eval_duration:.2f}s.")

    # Báo cáo phân loại chi tiết (Classification Report)
    report_dict = classification_report(
        y_test_multi,
        y_pred_multi,
        target_names=class_labels,
        digits=4,
        output_dict=True,
        zero_division=0
    )

    print("\n" + "=" * 88)
    print(f"{'LỚP HÀNH VI / HỌ MÃ ĐỘC':<24} | {'PRECISION':<12} | {'RECALL':<12} | {'F1-SCORE':<12} | {'SỐ MẪU TEST':<12}")
    print("=" * 88)

    multiclass_rows = []
    for cls_name in class_labels:
        metrics = report_dict[cls_name]
        p = metrics["precision"]
        r = metrics["recall"]
        f = metrics["f1-score"]
        s = int(metrics["support"])

        multiclass_rows.append({
            "Evaluation_Type": "Dedicated_Multiclass_Model",
            "Class_or_Family": cls_name,
            "Total_Samples": s,
            "Correct_Predictions": int(np.sum((y_test_multi == target_encoder.transform([cls_name])[0]) & (y_pred_multi == target_encoder.transform([cls_name])[0]))),
            "Precision": p,
            "Recall": r,
            "F1_Score": f,
            "Metric_Note": f"Precision={p*100:.2f}%, Recall={r*100:.2f}%, F1={f*100:.2f}%"
        })
        print(f"{cls_name:<24} | {p*100:>10.2f}% | {r*100:>10.2f}% | {f*100:>10.2f}% | {s:>12,}")

    print("=" * 88)
    print(f"{'Macro Average':<24} | {report_dict['macro avg']['precision']*100:>10.2f}% | {report_dict['macro avg']['recall']*100:>10.2f}% | {report_dict['macro avg']['f1-score']*100:>10.2f}% | {int(report_dict['macro avg']['support']):>12,}")
    print(f"{'Weighted Average':<24} | {report_dict['weighted avg']['precision']*100:>10.2f}% | {report_dict['weighted avg']['recall']*100:>10.2f}% | {report_dict['weighted avg']['f1-score']*100:>10.2f}% | {int(report_dict['weighted avg']['support']):>12,}")
    print("=" * 88)

    # Xuất toàn bộ kết quả vào CSV
    all_results = binary_recall_rows + multiclass_rows
    res_df = pd.DataFrame(all_results)
    res_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[+] ĐÃ LƯU TOÀN BỘ KẾT QUẢ ĐA LỚP & RECALL TỪNG HỌ VÀO: {OUTPUT_CSV}")

    # Vẽ ma trận nhầm lẫn (Confusion Matrix) đa lớp
    cm = confusion_matrix(y_test_multi, y_pred_multi)
    # Chuẩn hóa theo hàng để thấy rõ recall từng lớp
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    plt.figure(figsize=(10, 8), dpi=300)
    sns.heatmap(
        cm_norm * 100.0,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        xticklabels=class_labels,
        yticklabels=class_labels,
        cbar_kws={'label': 'Tỷ lệ nhận diện chuẩn hóa (%)'}
    )
    plt.title("Ma trận nhầm lẫn phân loại đa lớp IoT NIDS (Multiclass Confusion Matrix %)", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Nhãn dự đoán của mô hình (Predicted)", fontsize=11, fontweight='bold')
    plt.ylabel("Nhãn thực tế lưu lượng mạng (Ground Truth)", fontsize=11, fontweight='bold')
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_CM_FIG)
    plt.close()
    print(f"[+] Đã xuất biểu đồ Confusion Matrix đa lớp vào: {OUTPUT_CM_FIG}")

    return res_df


if __name__ == "__main__":
    run_multiclass_evaluation()
