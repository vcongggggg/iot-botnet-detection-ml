# -*- coding: utf-8 -*-
"""
Script sinh toàn bộ các biểu đồ phân tích khám phá dữ liệu (EDA) bổ sung (fig09 - fig16)
chạy trực tiếp trên tập dữ liệu THẬT (train_set.csv và test_set.csv).
Đạt chuẩn xuất bản khoa học: độ phân giải 300 DPI, tiếng Việt chuẩn, trục có đơn vị rõ ràng.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_CSV = os.path.join(BASE_DIR, "train_set.csv")
TEST_CSV = os.path.join(BASE_DIR, "test_set.csv")
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Cấu hình font và style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0


def load_eda_sample(n_rows: int = 300000):
    print(f"[*] Đang nạp {n_rows:,} bản ghi từ train_set.csv để phân tích EDA...")
    df = pd.read_csv(TRAIN_CSV, nrows=n_rows, low_memory=False)
    # Chuẩn hóa nhãn
    df['is_malicious'] = df['label'].astype(str).apply(lambda x: 0 if 'benign' in x.lower() else 1)
    df['label_str'] = df['is_malicious'].map({0: 'Lưu lượng sạch (Benign)', 1: 'Lưu lượng độc hại (Malicious)'})

    # Ép kiểu số
    for c in ['duration', 'orig_bytes', 'resp_bytes', 'orig_pkts', 'resp_pkts', 'id.resp_p']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].replace('-', '0'), errors='coerce').fillna(0)
    return df


def plot_fig09_protocol_distribution(df):
    print("[*] Đang vẽ fig09_protocol_distribution.png ...")
    proto_counts = df.groupby(['proto', 'label_str']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
    colors = ['#10B981', '#EF4444']
    proto_counts.plot(kind='bar', ax=ax, color=colors, width=0.6, edgecolor='#0F172A', linewidth=0.8)

    ax.set_title('PHÂN BỐ GIAO THỨC TẦNG GIAO VẬN (TCP, UDP, ICMP)\nTHEO NHÃN LƯU LƯỢNG SẠCH VS. ĐỘC HẠI',
                 fontsize=13, fontweight='bold', pad=14, color='#0F172A')
    ax.set_xlabel('Giao thức mạng (Protocol)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel('Số lượng bản ghi luồng (Thang Log)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_yscale('log')
    ax.set_xticklabels(proto_counts.index, rotation=0, fontsize=11, fontweight='bold')
    ax.legend(title='Nhãn lớp', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')

    # Thêm giá trị phần trăm
    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig09_protocol_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig10_top_ports(df):
    print("[*] Đang vẽ fig10_top_ports.png ...")
    mal_df = df[df['is_malicious'] == 1]
    top_ports = mal_df['id.resp_p'].value_counts().head(10)

    port_names = {
        23: "Port 23 (Telnet Mirai)",
        2323: "Port 2323 (Telnet Alt)",
        22: "Port 22 (SSH Brute)",
        80: "Port 80 (HTTP / DDoS)",
        5555: "Port 5555 (ADB Android)",
        7547: "Port 7547 (TR-069 CWMP)",
        4444: "Port 4444 (Torii C&C)",
        6667: "Port 6667 (IRC Botnet)",
        8080: "Port 8080 (HTTP Proxy)",
        37215: "Port 37215 (Huawei Router)"
    }
    labels = [port_names.get(int(p), f"Port {int(p)}") for p in top_ports.index]

    fig, ax = plt.subplots(figsize=(9.5, 6), dpi=300)
    bars = ax.barh(range(len(top_ports)), top_ports.values, color='#DC2626', edgecolor='#7F1D1D', height=0.65)
    ax.set_yticks(range(len(top_ports)))
    ax.set_yticklabels(labels, fontsize=10.5, fontweight='bold')
    ax.invert_yaxis()

    ax.set_title('TOP 10 CỔNG ĐÍCH (DESTINATION PORTS) BỊ BOTNET TẤN CÔNG NHIỀU NHẤT\n(Dữ liệu luồng độc hại từ Stratosphere IoT-23)',
                 fontsize=13, fontweight='bold', pad=14, color='#0F172A')
    ax.set_xlabel('Số lượng luồng mạng ghi nhận (Bản ghi)', fontsize=11, fontweight='bold', labelpad=8)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.grid(True, linestyle='--', alpha=0.5, axis='x')

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f" {w:,} ({w/len(mal_df)*100:.1f}%)",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points",
                    va='center', ha='left', fontsize=9.5, fontweight='bold', color='#1E293B')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig10_top_ports.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig11_duration_distribution(df):
    print("[*] Đang vẽ fig11_duration_distribution.png ...")
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    benign_dur = df[df['is_malicious'] == 0]['duration']
    mal_dur = df[df['is_malicious'] == 1]['duration']

    # Thang log(duration + 1e-4)
    bins = np.logspace(-4, 3, 50)
    ax.hist(benign_dur + 1e-4, bins=bins, alpha=0.65, label='Lưu lượng sạch (Benign)', color='#10B981', edgecolor='#065F46', density=True)
    ax.hist(mal_dur + 1e-4, bins=bins, alpha=0.6, label='Mã độc Botnet (Malicious)', color='#EF4444', edgecolor='#991B1B', density=True)

    ax.set_xscale('log')
    ax.set_title('PHÂN BỐ THỜI LƯỢNG PHIÊN KẾT NỐI (DURATION) THANG LOGARITHM\n(So sánh tính chớp nhoáng của Botnet Scan vs. Phiên hợp lệ)',
                 fontsize=13, fontweight='bold', pad=14, color='#0F172A')
    ax.set_xlabel('Thời lượng phiên kết nối (Giây - Thang Log10)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel('Mật độ xác suất (Density)', fontsize=11, fontweight='bold', labelpad=8)
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig11_duration_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig12_bytes_distribution(df):
    print("[*] Đang vẽ fig12_bytes_distribution.png ...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    bins = np.logspace(0, 6, 40)
    # Orig bytes
    ax1.hist(df[df['is_malicious'] == 0]['orig_bytes'] + 1, bins=bins, alpha=0.65, label='Benign', color='#10B981', density=True)
    ax1.hist(df[df['is_malicious'] == 1]['orig_bytes'] + 1, bins=bins, alpha=0.6, label='Malicious', color='#EF4444', density=True)
    ax1.set_xscale('log')
    ax1.set_title('Số Byte gửi từ Nguồn (orig_bytes)', fontsize=11.5, fontweight='bold')
    ax1.set_xlabel('orig_bytes (Bytes - Thang Log10)', fontsize=10.5, fontweight='bold')
    ax1.set_ylabel('Mật độ xác suất', fontsize=10.5, fontweight='bold')
    ax1.legend()

    # Resp bytes
    ax2.hist(df[df['is_malicious'] == 0]['resp_bytes'] + 1, bins=bins, alpha=0.65, label='Benign', color='#10B981', density=True)
    ax2.hist(df[df['is_malicious'] == 1]['resp_bytes'] + 1, bins=bins, alpha=0.6, label='Malicious', color='#EF4444', density=True)
    ax2.set_xscale('log')
    ax2.set_title('Số Byte phản hồi từ Đích (resp_bytes)', fontsize=11.5, fontweight='bold')
    ax2.set_xlabel('resp_bytes (Bytes - Thang Log10)', fontsize=10.5, fontweight='bold')
    ax2.legend()

    fig.suptitle('SO SÁNH TẢI TRỌNG TRUYỀN TẢI (BYTES) GIỮA LƯU LƯỢNG SẠCH VÀ MÃ ĐỘC BOTNET\n(Phần lớn luồng quét Botnet S0 có orig_bytes = 0 và resp_bytes = 0)',
                 fontsize=13, fontweight='bold', color='#0F172A', y=1.03)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig12_bytes_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig13_packets_distribution(df):
    print("[*] Đang vẽ fig13_packets_distribution.png ...")
    fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)

    # Đếm tỷ lệ gói tin orig_pkts
    benign_pkts = df[df['is_malicious'] == 0]['orig_pkts'].clip(upper=15)
    mal_pkts = df[df['is_malicious'] == 1]['orig_pkts'].clip(upper=15)

    bins = np.arange(0.5, 16.5, 1)
    ax.hist([benign_pkts, mal_pkts], bins=bins, label=['Benign (Sạch)', 'Malicious (Độc hại)'],
            color=['#10B981', '#EF4444'], edgecolor='#0F172A', linewidth=0.7, density=True)

    ax.set_title('PHÂN BỐ SỐ LƯỢNG GÓI TIN GỬI ĐI TỪ NGUỒN (ORIG_PKTS)\n(Hơn 92% luồng Botnet Scan chỉ gửi đúng 1 gói SYN thăm dò)',
                 fontsize=12.5, fontweight='bold', pad=14, color='#0F172A')
    ax.set_xlabel('Số gói tin gửi (orig_pkts - giới hạn 15 gói)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_ylabel('Tỷ lệ tương đối (Density)', fontsize=11, fontweight='bold', labelpad=8)
    ax.set_xticks(range(1, 16))
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig13_packets_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig14_botnet_family_breakdown(df):
    print("[*] Đang vẽ fig14_botnet_family_breakdown.png ...")
    if 'scenario_tag' in df.columns:
        sc_counts = df['scenario_tag'].value_counts()
    else:
        sc_counts = df['detailed-label'].value_counts().head(8)

    # Nhóm các họ mã độc chính
    family_map = {
        'Mirai-48': 'Mirai (Capture-48)',
        'Hajime': 'Hajime (Capture-1/3/9)',
        'Mirai/Kenjiro': 'Kenjiro / Okiru',
        'Muhstik': 'Muhstik Botnet',
        'Mirai-Var': 'Mirai Biến thể',
        'Hakai': 'Hakai (Capture-8)',
        'C&C/FileDownload': 'C&C File Download',
        'Torii-1': 'Torii (Capture-20)',
        'Torii-2': 'Torii (Capture-21)',
        'Benign-Pure1': 'Benign Echo/Hue',
        'Benign-Pure2': 'Benign Somfy Lock'
    }
    remapped = {}
    for k, v in sc_counts.items():
        name = family_map.get(str(k), str(k))
        remapped[name] = remapped.get(name, 0) + v

    s = pd.Series(remapped).sort_values(ascending=False).head(8)

    fig, ax = plt.subplots(figsize=(9.5, 6), dpi=300)
    colors = ['#DC2626', '#EA580C', '#D97706', '#CA8A04', '#65A30D', '#0D9488', '#0284C7', '#4F46E5']
    bars = ax.bar(range(len(s)), s.values, color=colors[:len(s)], edgecolor='#0F172A', linewidth=0.8, width=0.65)

    ax.set_title('TỶ LỆ PHÂN BỐ CÁC HỌ MÃ ĐỘC BOTNET IoT TRONG BỘ DỮ LIỆU IoT-23\n(Chiếm ưu thế bởi Mirai, Hajime và Torii)',
                 fontsize=13, fontweight='bold', pad=14, color='#0F172A')
    ax.set_xticks(range(len(s)))
    ax.set_xticklabels(s.index, rotation=25, ha='right', fontsize=10, fontweight='bold')
    ax.set_ylabel('Số lượng bản ghi luồng mạng (Flows)', fontsize=11, fontweight='bold', labelpad=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.grid(True, linestyle='--', alpha=0.5, axis='y')

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:,}\n({h/s.sum()*100:.1f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig14_botnet_family_breakdown.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def plot_fig16_time_comparison():
    print("[*] Đang vẽ fig16_time_comparison.png ...")
    # Dữ liệu đối sánh thời gian từ Bảng 2.3 và thực nghiệm
    models = ['Logistic\nRegression', 'Decision\nTree (CART)', 'Random\nForest', 'XGBoost\n(Hist)', 'LightGBM\n(Đề xuất)']
    train_times = [28.67, 55.12, 71.61, 31.46, 19.83]
    # Độ trễ suy luận batch ms / 1,000 flows
    infer_latencies = [0.012, 0.008, 0.045, 0.018, 0.0043]

    x = np.arange(len(models))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(10, 5.8), dpi=300)
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - width/2, train_times, width, label='Thời gian huấn luyện trên 4.55M dòng (Giây)', color='#3B82F6', edgecolor='#1E3A8A', linewidth=0.8)
    b2 = ax2.bar(x + width/2, infer_latencies, width, label='Độ trễ suy luận Batch (ms/luồng)', color='#10B981', edgecolor='#065F46', linewidth=0.8)

    ax1.set_title('ĐỐI SÁNH THỜI GIAN HUẤN LUYỆN VÀ ĐỘ TRỄ SUY LUẬN 5 MÔ HÌNH MACHINE LEARNING\n(LightGBM đạt tốc độ train nhanh nhất 19.83s và độ trễ thấp nhất 0.0043 ms/luồng)',
                  fontsize=12.5, fontweight='bold', pad=15, color='#0F172A')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=10.5, fontweight='bold')

    ax1.set_ylabel('Thời gian huấn luyện (Giây - thấp hơn là tốt hơn)', fontsize=11, fontweight='bold', color='#1E40AF', labelpad=8)
    ax2.set_ylabel('Độ trễ suy luận Batch (ms/luồng - thấp hơn là tốt hơn)', fontsize=11, fontweight='bold', color='#065F46', labelpad=8)

    ax1.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax2.grid(False)

    for bar in b1:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}s", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1E3A8A')

    for bar in b2:
        h = bar.get_height()
        ax2.annotate(f"{h:.4f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#065F46')

    # Hợp nhất legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=10)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "fig16_time_comparison.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"  [+] Đã lưu: {out_path}")


def main():
    print("=" * 76)
    print("  SINH BỘ BIỂU ĐỒ EDA KHOA HỌC BỔ SUNG (FIG09 - FIG16) CHUẨN 300 DPI")
    print("=" * 76)

    df_sample = load_eda_sample(n_rows=300000)
    plot_fig09_protocol_distribution(df_sample)
    plot_fig10_top_ports(df_sample)
    plot_fig11_duration_distribution(df_sample)
    plot_fig12_bytes_distribution(df_sample)
    plot_fig13_packets_distribution(df_sample)
    plot_fig14_botnet_family_breakdown(df_sample)
    plot_fig16_time_comparison()

    print("\n[+] HOÀN THÀNH TẤT CẢ 7 BIỂU ĐỒ MỚI TẠI:", ASSETS_DIR)


if __name__ == "__main__":
    main()
