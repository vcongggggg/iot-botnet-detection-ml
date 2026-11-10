# IoT Botnet Detection & Classification System using Machine Learning (Stratosphere IoT-23)
> **Đồ án Cuối kỳ Học phần:** Kiểm thử Xâm nhập (Penetration Testing)  
> **Đơn vị đào tạo:** Khoa Công nghệ Thông tin — Trường Đại học Bách Khoa, Đại học Đà Nẵng  
> **Nhóm thực hiện:** Nhóm 4  
> - **Nguyễn Công Minh** — SĐT: `0825385889`  
> - **Ngô Văn Công** — SĐT: `0775745371`  
> **Repository:** `https://github.com/vcongggggg/iot-botnet-detection-ml`  

---

## 1. TỔNG QUAN ĐỀ TÀI

Hệ sinh thái Internet vạn vật (IoT) bùng nổ với hàng tỷ thiết bị camera IP, router thông minh, cảm biến công nghiệp nhưng thường có cấu hình phần cứng yếu và thiếu hụt cơ chế bảo mật cơ bản (mật khẩu mặc định cứng, mở dịch vụ Telnet/SSH không mã hóa). Điều này biến các thiết bị IoT thành mục tiêu lây nhiễm hàng đầu của các mạng máy tính ma (Botnet) nguy hiểm như **Mirai**, **Hajime**, và **Torii**.

Đề tài này xây dựng giải pháp phòng vệ mạng cấp độ cổng biên (**AI NIDS/IPS**):
1. **Huấn luyện & Đánh giá trên 100% dữ liệu lớn (Big Data ML):** Xử lý toàn bộ **5.696.295 bản ghi** luồng mạng Zeek Conn-Log của bộ dữ liệu quốc tế **Stratosphere IoT-23** (Đại học Kỹ thuật Séc - CTU).
2. **Quy trình chuẩn quốc tế chống Data Leakage:** Áp dụng chia tách phân tầng **Stratified Train-Test Split 80/20** (`4.557.036` dòng Train / `1.139.259` dòng Test độc lập). Bộ mã hóa `OrdinalEncoder` và chuẩn hóa `StandardScaler` chỉ được `fit` trên tập Train và `transform` sang tập Test.
3. **Thực nghiệm đối sánh 5 thuật toán Machine Learning:** Logistic Regression, Decision Tree, Random Forest, XGBoost và **LightGBM** (mô hình tối ưu nhất đạt **Accuracy 99.99%**, **F1-Score 99.99%**, tốc độ suy luận batch `0.0043 ms/flow`).
4. **Hệ thống Giả lập Tấn công - Phòng thủ 3 Bên Thời gian thực (Live 3-Tier Testbed):**
   - **Bên 1: Kẻ tấn công (Red Team Botnet Console - Cổng 9090):** Phát động 4 kịch bản Botnet Kill-Chain hoặc dùng công cụ Kali Linux (`nmap`, `hydra`, `hping3`).
   - **Bên 2: Trạm gác AI NIDS (Admin SOC Dashboard - Cổng 5000):** Giám sát lưu lượng mạng, phân loại hành vi Botnet và tự động chặn IP qua **IPS Auto-Block**.
   - **Bên 3: Thiết bị IoT Nạn nhân (Victim Smart Camera - Cổng 8088 & Telnet 2323):** Giả lập camera `DUT-SmartCam-Pro-X1` phục vụ người dùng và phát sinh lưu lượng hợp lệ (Benign).

---

## 2. KIẾN TRÚC HỆ THỐNG VÀ DANH MỤC HÌNH ẢNH KHOA HỌC (300 DPI)

Toàn bộ các biểu đồ và sơ đồ kiến trúc chuẩn khoa học 300 DPI được lưu trữ trong thư mục `report_assets/`:
- `fig1_system_architecture.png`: Kiến trúc tổng thể hệ thống phòng vệ AI NIDS và giả lập 3 bên.
- `fig2_class_distribution.png`: Phân bố nhãn lớp Benign (8,74%) và Malicious (91,26%) trên 5.696.295 bản ghi.
- `fig3_conn_state_analysis.png`: Phân tích khám phá dữ liệu (EDA): Phân bố trạng thái kết nối Zeek (`S0`, `SF`...) và giao thức mạng.
- `fig4_feature_importance.png`: Mức độ đóng góp đặc trưng (Feature Importance) trong mô hình LightGBM (Cổng đích `id.resp_p` dẫn đầu).
- `fig5_model_benchmark.png`: Biểu đồ đối sánh hiệu năng (Accuracy, Precision, Recall, F1) và thời gian huấn luyện 5 mô hình ML.
- `fig6_confusion_matrix.png`: Ma trận nhầm lẫn (Confusion Matrix) của LightGBM trên 1.139.259 dòng kiểm thử độc lập (TN=99.472, FP=120, FN=18, TP=1.039.649).
- `fig7_traffic_asymmetry.png`: Phân tích bất đối xứng lưu lượng mạng: Gói tin gửi (orig_pkts) vs Gói tin nhận (resp_pkts).
- `fig8_live_soc_simulation.png`: Kết quả thực nghiệm hệ thống giả lập 3 bên theo thời gian thực (32 luồng demo).
- `fig15_roc_curves.png`: Đường cong ROC và chỉ số AUC đối sánh thực tế cả 5 mô hình ML (LightGBM AUC = 0.99998, Random Forest = 0.99999, XGBoost = 0.99983, Decision Tree = 0.99925, Logistic Regression = 0.98577).

---

## 3. KẾT QUẢ ĐỐI SÁNH 5 MÔ HÌNH MACHINE LEARNING (IoT-23 DATASET)

| TT | Mô hình Học máy | Accuracy | Precision | Recall | F1-Score | Thời gian Train (4,55M dòng) | Đánh giá Kỹ thuật |
| :-: | :--- | :-: | :-: | :-: | :-: | :-: | :--- |
| 1 | **Logistic Regression** | `98.32%` | `98.82%` | `99.34%` | `99.08%` | `28.67 giây` | Tuyến tính, bỏ sót luồng C&C phi tuyến |
| 2 | **Decision Tree (CART)** | `99.99%` | `99.99%` | `100.00%` | `100.00%` | `55.12 giây` | Độ chính xác rất cao nhưng cây đơn dễ Overfit |
| 3 | **Random Forest** | `99.90%` | `99.89%` | `100.00%` | `99.95%` | `71.61 giây` | Ổn định nhưng thời gian huấn luyện chậm nhất |
| 4 | **XGBoost (Hist Tree)** | `99.90%` | `99.90%` | `100.00%` | `99.95%` | `31.46 giây` | Hiệu năng cao, tốc độ huấn luyện khá nhanh |
| 5 | **LightGBM (Đề xuất)** | **`99.99%`** | **`99.99%`** | **`100.00%`** | **`99.99%`** | **`19.83 giây`** | **Ngang Decision Tree về độ chính xác, nhanh nhất khi train (19.83s so với 55.12s), chống quá khớp vượt trội** |

### Đánh giá trên 1.139.259 dòng Test độc lập (Notebook 02):
- **True Positives (TP):** `1.039.649 / 1.039.667` luồng độc hại được phát hiện (Tỷ lệ Recall = **`99.9983%`**, chỉ có **FN = 18** luồng).
- **True Negatives (TN):** `99.472 / 99.592` luồng hợp lệ được phân loại đúng (Tỷ lệ **FP = 120** luồng, tương ứng FPR = **`0.12%`**), triệt tiêu báo động giả và quá tải cảnh báo (Alert Fatigue).
- **Tốc độ suy luận (Inference Latency):**
  - Đo batch trên 1.139.259 dòng test: **`0.0043 ms/luồng`** (~232.977 luồng/giây).
  - Đo batch mẫu 5.000 dòng test: **`0.0014 – 0.0029 ms/luồng`**.
  - Xử lý từng luồng đơn lẻ qua HTTP REST API: **`< 0.5 ms/luồng`**.

---

## 4. HƯỚNG DẪN CHẠY NHANH KIỂM ĐỊNH & DEMO

### 4.1. Lệnh Kiểm định Nhanh cho Reviewer / Auditor Agent (< 5 giây):
```bash
python test_quick_audit.py
```
Lệnh này kiểm tra toàn bộ artifact, nạp mô hình `iot_nids_bundle.joblib` và kiểm thử mù trên `sample_test_data/sample_test_flows_5000.csv`.

### 4.2. Khởi chạy Hệ thống Demo 3 Bên (1-Click trên Windows):
Nhấp đúp chuột vào file:
```bat
start_demo_3_ben.bat
```
Hệ thống tự động bật 3 dịch vụ và mở 3 tab trình duyệt:
1. **Bên 1: Red Team Attacker Console (`:9090`):** `http://127.0.0.1:9090`
2. **Bên 2: Admin SOC Dashboard (`:5000`):** `http://127.0.0.1:5000`
3. **Bên 3: Victim IoT Device (`:8088` & Telnet `:2323`):** `http://127.0.0.1:8088`

Xem chi tiết kịch bản 4 bước bảo vệ và cách chạy 2 laptop qua LAN/Wi-Fi tại: [HUONG_DAN_DEMO_VA_BAO_VE.md](HUONG_DAN_DEMO_VA_BAO_VE.md).

---

## 5. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
├── 01_IoT23_EDA_and_Training.ipynb           # Notebook EDA & Train 5 mô hình trên 4.55M dòng
├── 02_IoT23_Model_Evaluation_and_Testing.ipynb # Notebook Test độc lập trên 1.14M dòng
├── Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx   # Báo cáo Word chuẩn 100% FORM_BAOCAO.pptx
├── Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx # Slide PowerPoint Widescreen 16:9
├── HUONG_DAN_DEMO_VA_BAO_VE.md               # Sổ tay Demo 3 bên & Kịch bản trả lời phản biện
├── AUDIT_CHECKLIST.md                         # Hướng dẫn và tiêu chí kiểm toán cho Auditor Agent
├── test_quick_audit.py                        # Script tự động audit toàn bộ hệ thống
├── benchmark_results.csv                      # Kết quả benchmark định lượng 5 mô hình (khớp Bảng 2.3)
├── roc_auc_results.csv                        # Kết quả tính toán ROC-AUC thật của 5 mô hình
├── iot_nids_bundle.joblib                     # Model LightGBM đóng gói kèm Encoders/Scaler
├── start_demo_3_ben.bat                       # Script 1-Click khởi chạy toàn bộ 3 phân hệ
├── scripts/                                   # Các script hỗ trợ kiểm chứng & tiền xử lý
│   ├── split_iot23.py                         # Phân chia Stratified 80/20 từ dữ liệu gốc
│   ├── sample_test_flows.py                   # Trích xuất 5.000 luồng test kiểm thử mù
│   └── compute_roc.py                         # Tính toán ROC/AUC và vẽ biểu đồ fig15
├── docs/                                      # Tài liệu học phần: Đề cương & Bảng đăng ký
│   ├── DeCuong_PenTest_DUT.pdf
│   └── DANHSACHPENTEST.xlsx
├── sample_test_data/                          # Dữ liệu mẫu phục vụ audit độc lập (5.000 flows)
│   └── sample_test_flows_5000.csv
├── report_assets/                             # Các biểu đồ khoa học chuẩn in ấn 300 DPI
│   ├── fig1_system_architecture.png
│   ├── fig2_class_distribution.png
│   ├── fig3_conn_state_analysis.png
│   ├── fig4_feature_importance.png
│   ├── fig5_model_benchmark.png
│   ├── fig6_confusion_matrix.png
│   ├── fig7_traffic_asymmetry.png
│   ├── fig8_live_soc_simulation.png
│   └── fig15_roc_curves.png
└── live_demo/                                 # Mã nguồn Hệ thống Giả lập 3 Phân hệ
    ├── attacker_botnet_console.py             # Bên 1: Kẻ tấn công Red Team Console (:9090)
    ├── ai_nids_guardian_server.py             # Bên 2: Trạm gác AI NIDS / Admin SOC (:5000)
    └── victim_iot_server.py                   # Bên 3: Thiết bị IoT Nạn nhân (:8088 / :2323)
```

---

## 6. TÀI LIỆU THAM KHẢO CHÍNH THỐNG
[1] S. Garcia, A. Parmisano, and M. J. Erquiaga, "IoT-23: A labeled dataset with malicious and benign IoT network traffic," Stratosphere Laboratory, CTU in Prague, 2020.  
[2] M. Antonakakis et al., "Understanding the Mirai Botnet," USENIX Security 17, pp. 1093–1110, 2017.  
[3] G. Ke et al., "LightGBM: A Highly Efficient Gradient Boosting Decision Tree," NeurIPS 30, pp. 3146–3154, 2017.  
[4] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," ACM KDD '16, pp. 785–794, 2016.  
[5] S. Edwards and I. Profetis, "Hajime: Analysis of a decentralized internet worm for IoT devices," Rapidity Networks, 2016.  
[6] J. Neduchal, M. Hron, and A. Caruso, "Torii Botnet: Not Another Mirai Variant," Avast Threat Labs, Sept. 2018.  
[7] V. Paxson, "Bro: A system for detecting network intruders in real-time," Computer Networks, vol. 31, pp. 2435–2463, 1999.  
[8] L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.  
[9] Y. Meidan et al., "N-BaIoT: Network-Based Detection of IoT Botnet Attacks Using Deep Autoencoders," IEEE Pervasive Computing, 2018.  
[10] N. Koroniotis et al., "Towards the development of realistic botnet dataset in the Internet of Things: Bot-IoT dataset," FGCS, 2019.
