# BẢNG KÊ KHAI DỮ LIỆU & HÌNH ẢNH TRÌNH CHIẾU SLIDE (MANIFEST)
## HỆ THỐNG PHÁT HIỆN XÂM NHẬP IoT-NIDS (STRATOSPHERE IoT-23)

- **Mục đích:** Cung cấp đầy đủ số liệu thực nghiệm định lượng mới và các biểu đồ khoa học độ phân giải cao (300 DPI, nền trắng, nhãn trục rõ ràng) phục vụ thiết kế bộ Slide thuyết trình đề tài.
- **Cam kết chất lượng:** 100% hình ảnh và số liệu được sinh ra từ các lần chạy thật trên máy trạm cục bộ, không dùng số liệu ước lượng, không sử dụng file mẫu giả.
- **Ngày tạo lập:** 13/11/2026

---

## 1. DANH MỤC 6 TẬP TIN HÌNH ẢNH TRONG THƯ MỤC `figures_slide/`

| STT | Tên Tập Tin | Độ Phân Giải / Định Dạng | Nội Dung Trực Quan Hóa | Nguồn Dữ Liệu Thực Nghiệm | Lệnh Tái Sinh Dữ Liệu |
|---|---|---|---|---|---|
| **1** | `demo_scenarios.png` | 3421 x 1770 (300 DPI, PNG) | Biểu đồ thanh ngang tỷ lệ chặn thực tế (Blocked / Total Flows) theo 5 kịch bản diễn tập phòng thủ 3 bên: Benign SmartHome (0/4 chặn, 100% pass), Credential Brute-Force (6/6 chặn, 100%), Hajime DDoS (10/10 chặn, 100%), Mirai Port Scan (4/8 chặn, 50%), Torii C&C (1/4 chặn, 25%). | Kết quả trung bình từ 3 lần chạy liên tiếp chế độ `--auto-demo` của hệ thống Live 3-Tier Demo (Attacker -> Guardian -> Victim). | `python scripts/run_demo_and_capture.py` |
| **2** | `per_family_recall.png` | 2993 x 1620 (300 DPI, PNG) | Biểu đồ thanh ngang tỷ lệ phát hiện (Recall) chi tiết theo từng họ mã độc và dạng hành vi trên 1.14M luồng test: PortScan (100.0%), DDoS (99.97%), C&C (99.87%), Brute-force (99.60%), Benign (99.88% TNR), Torii C&C (0.00% bị bỏ sót trong tập test ngẫu nhiên). | Bảng dữ liệu định lượng tại `multiclass_evaluation_results.csv` sinh từ tập kiểm thử `test_set.csv`. | `python scripts/generate_slide_figures_task2.py` |
| **3** | `ood_results.png` | 4165 x 1631 (300 DPI, PNG) | Biểu đồ đường cong kép đối sánh kiểm thử ngoài miền (OOD) trên Botnet Torii (Capture 20-1 & 21-1, 6,495 luồng): (A) ROC Curve minh họa ảo tưởng ROC-AUC (~0.97) khi lớp đa số áp đảo; (B) PR-AUC Curve minh họa sự sụt giảm trung thực của PR-AUC (1.0000 -> 0.5296) khi gặp Torii C&C. | Bảng dữ liệu định lượng tại `ood_evaluation_results.csv` trích xuất từ 2 kịch bản Torii nguyên bản. | `python scripts/generate_slide_figures_task2.py` |
| **4** | `ablation.png` | 3096 x 1620 (300 DPI, PNG) | Biểu đồ thanh ngang phân tích độ nhạy cắt bỏ đặc trưng (Ablation Study) trên 1.14M luồng test: F1 sụt giảm cực mạnh (-99.47%) khi ẩn nhóm số học hoặc nhóm phân loại (proto, conn_state, history), chứng minh mô hình phụ thuộc vào tương quan cổng đích và lịch sử TCP. | Bảng dữ liệu định lượng tại `ablation_study_results.csv` sinh từ việc zero-out các nhóm cột trên `test_set.csv`. | `python scripts/generate_slide_figures_task2.py` |
| **5** | `dashboard_demo.png` | 1774 x 1060 (Ảnh chụp thật, PNG) | Ảnh chụp màn hình thực tế giao diện SOC Web Dashboard (cổng :5000) của Trạm gác AI NIDS Guardian Server sau khi kết thúc 3 lượt diễn tập 5 kịch bản: hiển thị biểu đồ phân loại, thống kê thời gian thực và bảng các địa chỉ IP độc hại đã bị đưa vào danh sách đen (Blacklist). | Render thực tế từ Flask Web UI qua Headless Edge WebDriver tại `http://127.0.0.1:5000`. | `python scripts/run_demo_and_capture.py` |
| **6** | `attacker_console.png` | 1574 x 860 (Ảnh chụp thật, PNG) | Ảnh chụp màn hình thực tế giao diện điều khiển tấn công Attacker Botnet Console (cổng :9090): bảng điều khiển phát động 5 kịch bản tấn công Red Team và theo dõi phản hồi từ Guardian Server. | Render thực tế từ Attacker Web Console qua Headless Edge WebDriver tại `http://127.0.0.1:9090`. | `python scripts/run_demo_and_capture.py` |

---

## 2. BẢNG SỐ LIỆU ĐỐI SÁNH 5 MÔ HÌNH MACHINE LEARNING (MỤC 1)

Số liệu huấn luyện lại đầy đủ trên toàn bộ 4,557,036 dòng dữ liệu `train_set.csv` với bộ siêu tham số chuẩn hóa đồng bộ 100% (LR 200, DT 12, RF 25 cây, XGBoost 100/6/0.1, LightGBM 100/6/0.1):

| Thuật Toán | Siêu Tham Số Chuẩn | Accuracy | Precision | Recall | F1-Score | Train Time (s) | File Kết Quả |
|---|---|---|---|---|---|---|---|
| **Logistic Regression** | `max_iter=200` | 98.84% | 99.29% | 99.44% | 99.36% | 5.66s | `benchmark_results.csv` |
| **Decision Tree** | `max_depth=12` | 99.99% | 99.99% | 100.00% | 100.00% | 24.28s | `benchmark_results.csv` |
| **Random Forest** | `n_estimators=25, max_depth=12` | 99.89% | 99.88% | 100.00% | 99.94% | 41.53s | `benchmark_results.csv` |
| **XGBoost (Hist)** | `n_estimators=100, max_depth=6, lr=0.1` | 99.98% | 99.98% | 100.00% | 99.99% | 22.97s | `benchmark_results.csv` |
| **LightGBM (Đề xuất)**| `n_estimators=100, max_depth=6, lr=0.1` | **99.99%** | **99.99%** | **100.00%** | **100.00%** | **15.85s** | `benchmark_results.csv` |

*Bảng xếp hạng diện tích ROC-AUC kiểm thử độc lập (50,000 mẫu test):*
- LightGBM: **1.000000**
- Random Forest: **0.999977**
- XGBoost: **0.999879**
- Decision Tree: **0.999363**
- Logistic Regression: **0.986937**
*(Lưu tại `roc_auc_results.csv` và `report_assets/fig15_roc_curves.png`)*

---

## 3. THỐNG KÊ CHI TIẾT 3 LẦN CHẠY DEMO DIỄN TẬP PHÒNG THỦ (MỤC 2)

Kết quả đo lường khách quan 100% không dùng Hint (Guardian quyết định hoàn toàn bằng mô hình):

| Kịch Bản Diễn Tập | Số Luồng Gửi | Lần 1 (Chặn/Sót) | Lần 2 (Chặn/Sót) | Lần 3 (Chặn/Sót) | Tỷ Lệ Chặn Trung Bình | Đánh Giá Phòng Thủ |
|---|---|---|---|---|---|---|
| **0. Benign SmartHome Traffic** | 4 | 0 / 4 | 0 / 4 | 0 / 4 | **0.0% Chặn** (100% Pass) | **Hoàn hảo:** 0% Báo động giả (False Positive) |
| **1. Mirai Horizontal Port Scan** | 8 | 4 / 4 | 4 / 4 | 4 / 4 | **50.0% Chặn** (4/8) | Chặn các cổng Telnet/SSH/8080 quen thuộc; Bỏ sót các cổng chưa từng thấy trong train (80, 5555, 7547, 37215) - model phụ thuộc cổng đích (id.resp_p), không phải cờ TCP (cả luồng bắt và sót đều S0) |
| **2. Telnet Credential Brute-Force** | 6 | 6 / 0 | 6 / 0 | 6 / 0 | **100.0% Chặn** (6/6) | **Chặn tuyệt đối 100%** lưu lượng dò mật khẩu |
| **3. Torii C&C Reverse Shell** | 4 | 1 / 3 | 1 / 3 | 1 / 3 | **25.0% Chặn** (1/4) | Chặn cổng 6667 (IRC); Bỏ sót cổng 4444 (x2) và 8443 - các cổng này model chưa học, không liên quan cờ kết nối (cả 4 luồng đều S0) |
| **4. Hajime DDoS SYN Flood** | 10 | 10 / 0 | 10 / 0 | 10 / 0 | **100.0% Chặn** (10/10) | **Chặn tuyệt đối 100%** đợt flood gói tin |
| **TỔNG LƯỢNG ĐỘC HẠI** | **28** | **21 / 7** | **21 / 7** | **21 / 7** | **75.0% Chặn** (21/28) | Độ ổn định: Phương sai = 0 (100% xác định) |
