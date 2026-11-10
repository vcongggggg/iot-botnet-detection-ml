# -*- coding: utf-8 -*-
"""
Script phân chia bộ dữ liệu Stratosphere IoT-23 theo tỷ lệ chuẩn quốc tế Stratified 80/20.
Học phần: Kiểm thử Xâm nhập (Penetration Testing) - ĐH Bách Khoa, ĐH Đà Nẵng
Nhóm 4: Nguyễn Công Minh & Ngô Văn Công

LƯU Ý VỀ TÍNH TOÀN VẸN VÀ DUNG LƯỢNG KHO MÃ NGUỒN:
- Bộ dữ liệu IoT-23 gốc bao gồm 20 kịch bản mã độc (Malware captures) và 3 kịch bản
  lưu lượng hợp lệ (Benign captures) thu thập bởi Czech Technical University (CTU, 2020),
  tổng dung lượng giải nén vượt quá 8.8 GB (~21 GB file thô).
- Sau khi trích xuất và tiền xử lý, tập train_set.csv (775 MB) và test_set.csv (193 MB)
  có tổng quy mô 5.696.295 bản ghi.
- Theo quy định kích thước tập tin của Git và GitHub (giới hạn tối đa 100 MB/file),
  các file CSV và log thô này được cấu hình trong .gitignore và lưu trữ tại máy trạm
  huấn luyện cục bộ (hoặc tải trực tiếp từ Stratosphere Labs: https://www.stratosphereips.org/datasets-iot23).
- Script này cung cấp phương thức xác định tái tạo 100% hai tập train_set.csv và test_set.csv.
"""

import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT_CSV = os.path.join(BASE_DIR, "IoT23_Diverse_Combined_1GB.csv")
TRAIN_OUTPUT_CSV = os.path.join(BASE_DIR, "train_set.csv")
TEST_OUTPUT_CSV = os.path.join(BASE_DIR, "test_set.csv")

TARGET_COLS_12 = [
    'id.orig_p', 'id.resp_p', 'duration', 'orig_bytes', 'resp_bytes',
    'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes',
    'proto', 'conn_state', 'history', 'label'
]


def split_iot23_dataset(input_csv: str, train_out: str, test_out: str, random_state: int = 42):
    print("=" * 76)
    print("  CHIẾN LƯỢC CHIA TÁCH PHÂN TẦNG STRATIFIED 80/20 CHỐNG DATA LEAKAGE")
    print(f"  Nguồn dữ liệu: {input_csv}")
    print("=" * 76)

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Không tìm thấy file nguồn: {input_csv}")

    t0 = time.time()
    print("[*] Đang đọc toàn bộ dữ liệu IoT-23...")
    df = pd.read_csv(input_csv, low_memory=False)
    total_rows = len(df)
    print(f"[+] Đã nạp thành công {total_rows:,} bản ghi trong {time.time() - t0:.2f}s.")

    # Chuẩn hóa nhãn nhị phân
    target_col = 'label' if 'label' in df.columns else df.columns[-1]
    df['target_binary'] = df[target_col].astype(str).apply(
        lambda x: 0 if 'benign' in x.lower() else 1
    )

    class_counts = df['target_binary'].value_counts()
    print(f"[*] Phân bố toàn cục: Benign (0)={class_counts.get(0, 0):,} ({class_counts.get(0, 0)/total_rows*100:.2f}%), "
          f"Malicious (1)={class_counts.get(1, 0):,} ({class_counts.get(1, 0)/total_rows*100:.2f}%)")

    # Chia tách phân tầng Stratified 80/20
    print(f"\n[*] Đang thực thi train_test_split(test_size=0.2, random_state={random_state}, stratify=target)...")
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=random_state,
        stratify=df['target_binary']
    )

    # Loại bỏ cột phụ trợ
    train_df = train_df.drop(columns=['target_binary'])
    test_df = test_df.drop(columns=['target_binary'])

    print(f"[+] Tập Train (80%): {len(train_df):,} dòng.")
    print(f"[+] Tập Test  (20%): {len(test_df):,} dòng.")

    # Lưu kết quả
    print(f"\n[*] Đang ghi tập Train ra: {train_out} ...")
    train_df.to_csv(train_out, index=False)
    print(f"[*] Đang ghi tập Test  ra: {test_out} ...")
    test_df.to_csv(test_out, index=False)

    print("\n[+] HOÀN THÀNH CHIA TÁCH THÀNH CÔNG!")
    print(f"    - Train set: {train_out} ({os.path.getsize(train_out) / (1024*1024):.2f} MB)")
    print(f"    - Test set:  {test_out} ({os.path.getsize(test_out) / (1024*1024):.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Chia tách Stratified 80/20 cho bộ dữ liệu Stratosphere IoT-23")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_CSV, help="File CSV nguồn")
    parser.add_argument("--train-out", type=str, default=TRAIN_OUTPUT_CSV, help="File train đầu ra")
    parser.add_argument("--test-out", type=str, default=TEST_OUTPUT_CSV, help="File test đầu ra")
    parser.add_argument("--seed", type=int, default=42, help="Random seed phân tầng")
    args = parser.parse_args()

    split_iot23_dataset(args.input, args.train_out, args.test_out, random_state=args.seed)


if __name__ == "__main__":
    main()

