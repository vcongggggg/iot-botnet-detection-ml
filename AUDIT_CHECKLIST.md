# INDEPENDENT AUDIT GUIDE & VERIFICATION FRAMEWORK
**Đề tài:** Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT (Mirai, Hajime, Torii) sử dụng Machine Learning  
**Học phần:** Kiểm thử xâm nhập (Penetration Testing) — ĐH Bách Khoa, ĐH Đà Nẵng  
**Nhóm thực hiện:** Nhóm 4 — Nguyễn Công Minh (`0825385889`) & Ngô Văn Công (`0775745371`)  
**Repository:** `https://github.com/vcongggggg/iot-botnet-detection-ml`  

---

## 1. DÀNH CHO AGENT / AUDITOR ĐỘC LẬP (QUICK START AUDIT)

Để thẩm định nhanh toàn bộ đề tài, chạy lệnh sau tại thư mục gốc của repository:
```bash
python test_quick_audit.py
```
Script sẽ tự động kiểm tra:
1. Tính toàn vẹn của Báo cáo Word (`Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx`), Slide PowerPoint (`Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx`) và 8 biểu đồ khoa học 300 DPI trong `report_assets/`.
2. Kiểm tra mô hình `iot_nids_bundle.joblib` (LGBMClassifier kèm Encoders và Scaler).
3. Đánh giá kiểm thử mù trên `sample_test_data/sample_test_flows_5000.csv` (đo Accuracy, F1-Score, Confusion Matrix, và độ trễ suy luận mili-giây).
4. Xác minh sự sẵn sàng của hệ thống giả lập Tấn công - Phòng thủ 3 bên.

---

## 2. NỘI DUNG VÀ TIÊU CHÍ THẨM ĐỊNH (AUDIT MATRIX)

### Tiêu chí 1: Phòng chống rò rỉ dữ liệu (Anti-Data Leakage & Stratified 80/20 Split)
- **Vấn đề lịch sử:** Nhiều nghiên cứu trước đây chia Train/Test theo từng file log riêng lẻ khiến tập Train bị thiếu nhãn `Benign` (100% Malicious) dẫn tới học vẹt.
- **Giải pháp của đề tài:**
  - Hợp nhất toàn bộ `5.696.295` dòng của Stratosphere IoT-23 và chia tách phân tầng (**Stratified Split 80/20** với `random_state=42`).
  - **Tập Train (80%):** `4.557.036` dòng (`4.158.670` Malicious — 91,26% | `398.366` Benign — 8,74%).
  - **Tập Test độc lập (20%):** `1.139.259` dòng (`1.039.667` Malicious — 91,26% | `99.592` Benign — 8,74%).
  - `OrdinalEncoder` và `StandardScaler` **chỉ được `fit` trên tập Train** và chỉ `transform` sang tập Test.
  - Loại bỏ hoàn toàn các trường định danh gây học vẹt tĩnh (`ts`, `uid`, `id.orig_h`, `id.resp_h`, `service`, `local_orig`, `local_resp`).

### Tiêu chí 2: Tính khách quan trong đối sánh thuật toán (5 Mô hình ML)
Thực nghiệm so sánh 5 thuật toán học máy từ cổ điển đến hiện đại trên cùng một tập dữ liệu Train/Test:
1. **Logistic Regression:** Accuracy 98.32%, F1 99.08%, Train time 28.67s.
2. **Decision Tree (CART):** Accuracy 99.99%, F1 100.00%, Train time 55.12s.
3. **Random Forest:** Accuracy 99.90%, F1 99.95%, Train time 71.61s.
4. **XGBoost (Hist):** Accuracy 99.90%, F1 99.95%, Train time 31.46s.
5. **LightGBM (Đề xuất):** Accuracy 99.99%, F1 99.99%, Train time 19.83s.
- **Lý do chọn LightGBM:** Kết hợp 100 cây Boosting (GOSS + EFB) chống quá khớp tốt hơn cây đơn lẻ, thời gian huấn luyện nhanh nhất và suy luận 1,14 triệu dòng Test chỉ mất 4.89 giây (~0.004 ms/flow).

### Tiêu chí 3: Hệ thống Giả lập Tấn công - Phòng thủ 3 Bên Thời gian thực
Hệ thống không phụ thuộc phần cứng vật lý, chạy linh hoạt trên 1 Laptop hoặc phân tán trên 2 Laptop qua Wi-Fi/LAN:
- **Bên 1 (Attacker Red Team - Cổng 9090):** Phát động 4 kịch bản Botnet Kill-Chain:
  1. Mirai Horizontal Port Scan (`conn_state=S0`, `orig_bytes=0`).
  2. Mirai Telnet Credential Brute-Force (dò mật khẩu cổng `2323`).
  3. Torii C&C Beaconing (kết nối máy chủ điều khiển cổng `4444`, `6667`, `8443`).
  4. Hajime/Mirai DDoS SYN/UDP Flood (bão gói tin tốc độ cao).
- **Bên 2 (Admin SOC Guardian - Cổng 5000):** Nạp `iot_nids_bundle.joblib`, suy luận luồng mạng thời gian thực (<0.5ms), phân loại hành vi Botnet và kích hoạt **IPS Auto-Block** tự động đưa IP kẻ tấn công vào Firewall Blacklist.
- **Bên 3 (Victim IoT Device - Cổng 8088 & Telnet 2323):** Giả lập Camera thông minh `DUT-SmartCam-Pro-X1`, cho phép người dùng xem cảm biến, định kỳ gửi lưu lượng sạch (Benign SF) và hiển thị cảnh báo khi bị tấn công.

### Tiêu chí 4: Chuẩn mực Học thuật & Báo cáo
- Báo cáo Word [Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx](file:///c:/Study/HocKy6/IoT_NIDS_Pipeline/Bao_Cao_Cuoi_Ky_IoT_Botnet_ML_Nhom4.docx) bám sát 100% bố cục `FORM_BAOCAO.pptx`:
  - Trang bìa chuẩn ĐH Bách Khoa - ĐH Đà Nẵng.
  - Bảng danh mục từ viết tắt (27 thuật ngữ chuẩn).
  - Bảng danh mục hình ảnh (8 hình) và bảng biểu (7 bảng).
  - Mở đầu (5 mục đầy đủ).
  - Chương 1 (Cơ sở lý thuyết và giải phẫu 3 họ Botnet).
  - Chương 2 (Đề xuất mô hình và thực nghiệm 5.696.295 dòng).
  - Chương 3 (Hệ thống giả lập 3 bên cho Admin, User và Red Team).
  - Kết luận và 16 Tài liệu tham khảo chuẩn IEEE.
- Slide Thuyết trình [Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx](file:///c:/Study/HocKy6/IoT_NIDS_Pipeline/Slide_Thuyet_Trinh_IoT_Botnet_ML_Nhom4.pptx) gồm 14 slides 16:9 Widescreen hiện đại.

---

## 3. LỆNH KIỂM CHỨNG TRỰC TIẾP HỆ THỐNG DEMO 3 BÊN

```bash
# Cách 1: Bật toàn bộ 3 bên trong 1 click trên Windows:
start_demo_3_ben.bat

# Cách 2: Chạy kiểm thử từng service:
# Terminal 1 - AI NIDS Guardian:
python live_demo/ai_nids_guardian_server.py --port 5000

# Terminal 2 - Victim IoT Server:
python live_demo/victim_iot_server.py --http-port 8088 --telnet-port 2323

# Terminal 3 - Red Team Attacker CLI Auto-Demo:
python live_demo/attacker_botnet_console.py --auto-demo
```
