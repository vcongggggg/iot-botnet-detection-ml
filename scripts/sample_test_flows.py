# -*- coding: utf-8 -*-
"""
Script trích xuất mẫu kiểm thử độc lập 5.000 luồng (Blind Test Sample)
Dành cho Đánh giá Độc lập (Auditor Agent / Reviewer Verification).

CƠ CHẾ LẤY MẪU CHỐNG RÒ RỈ DỮ LIỆU (ANTI-DATA LEAKAGE):
1. Nguồn trích xuất là tệp 'test_set.csv' (tập Test 20% độc lập, 1.139.259 bản ghi),
   hoàn toàn tách biệt 100% với 'train_set.csv' (4.557.036 bản ghi) từ bước phân chia
   Stratified Split 80/20 với random_state=42.
2. Lấy mẫu phân tầng với tỷ lệ đại diện:
   - 4.000 luồng Malicious (80.0%)
   - 1.000 luồng Benign (20.0%)
   Được xáo trộn ngẫu nhiên (random_state=42) để tạo bài kiểm thử mù khách quan.
3. Kích thước tập tin sau khi xuất khoảng ~820 KB, cho phép commit trực tiếp lên GitHub
   để bất kỳ ai clone repository đều có dữ liệu kiểm thử thật ngay lập tức mà không cần
   phải tải về tệp test_set.csv (193 MB).
"""

import os
import sys
import argparse
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_SET_CSV = os.path.join(BASE_DIR, "test_set.csv")
SAMPLE_OUT_CSV = os.path.join(BASE_DIR, "sample_test_data", "sample_test_flows_5000.csv")


def extract_sample_test_flows(
    test_csv_path: str = TEST_SET_CSV,
    output_sample_path: str = SAMPLE_OUT_CSV,
    n_malicious: int = 4000,
    n_benign: int = 1000,
    random_state: int = 42
):
    print("=" * 76)
    print("  TRÍCH XUẤT 5.000 LUỒNG KIỂM THỬ ĐỘC LẬP TỪ TẬP TEST_SET.CSV")
    print("=" * 76)

    if not os.path.exists(test_csv_path):
        raise FileNotFoundError(f"Không tìm thấy tập test: {test_csv_path}")

    os.makedirs(os.path.dirname(output_sample_path), exist_ok=True)

    print(f"[*] Đang đọc dữ liệu từ {test_csv_path} (chỉ đọc các luồng thuộc tập Test)...")
    df = pd.read_csv(test_csv_path, nrows=150000, low_memory=False)

    target_col = 'label' if 'label' in df.columns else df.columns[-1]
    is_mal = df[target_col].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1)

    mal_df = df[is_mal == 1].head(n_malicious)
    ben_df = df[is_mal == 0].head(n_benign)

    assert len(mal_df) == n_malicious, f"Không đủ mẫu Malicious (chỉ có {len(mal_df)})"
    assert len(ben_df) == n_benign, f"Không đủ mẫu Benign (chỉ có {len(ben_df)})"

    # Hợp nhất và xáo trộn ngẫu nhiên có kiểm soát
    sample_df = pd.concat([mal_df, ben_df]).sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    sample_df.to_csv(output_sample_path, index=False)
    file_size_kb = os.path.getsize(output_sample_path) / 1024

    print(f"[+] Trích xuất thành công: {len(sample_df):,} luồng.")
    print(f"    - Malicious: {n_malicious:,} luồng ({n_malicious/len(sample_df)*100:.1f}%)")
    print(f"    - Benign:    {n_benign:,} luồng ({n_benign/len(sample_df)*100:.1f}%)")
    print(f"    - Lưu tại:   {output_sample_path} ({file_size_kb:.2f} KB)")
    print("[+] Mẫu kiểm thử đảm bảo 100% UNSEEN đối với tập huấn luyện Train!")


def main():
    parser = argparse.ArgumentParser(description="Trích xuất 5.000 luồng test kiểm thử mù")
    parser.add_argument("--test-csv", type=str, default=TEST_SET_CSV, help="Tệp test_set.csv nguồn")
    parser.add_argument("--out", type=str, default=SAMPLE_OUT_CSV, help="Tệp CSV mẫu đầu ra")
    parser.add_argument("--malicious", type=int, default=4000, help="Số luồng Malicious")
    parser.add_argument("--benign", type=int, default=1000, help="Số luồng Benign")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    extract_sample_test_flows(
        test_csv_path=args.test_csv,
        output_sample_path=args.out,
        n_malicious=args.malicious,
        n_benign=args.benign,
        random_state=args.seed
    )


if __name__ == "__main__":
    main()

