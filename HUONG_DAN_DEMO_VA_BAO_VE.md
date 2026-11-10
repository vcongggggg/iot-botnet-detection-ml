# HƯỚNG DẪN CHẠY DEMO 3 BÊN, KỊCH BẢN THUYẾT TRÌNH & BẢO VỆ ĐỒ ÁN CUỐI KỲ
**Học phần:** Kiểm thử xâm nhập (Penetration Testing) — Khoa Công nghệ Thông tin, Trường Đại học Bách Khoa - Đại học Đà Nẵng  
**Đề tài:** Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT (Mirai, Hajime, Torii) sử dụng Machine Learning  
**Nhóm thực hiện:** Nhóm 4  
- **Nguyễn Công Minh** — SĐT: `0825385889`  
- **Ngô Văn Công** — SĐT: `0775745371`  

---

## PHẦN 1: THÔNG TIN ĐĂNG KÝ TRÊN GOOGLE SHEET CỦA LỚP
Copy nội dung dưới đây để điền vào file Google Sheets đăng ký đề tài (`DANHSACHPENTEST.xlsx`):

- **Nhóm:** Nhóm 4
- **Thành viên 1:** Nguyễn Công Minh (`0825385889`)
- **Thành viên 2:** Ngô Văn Công (`0775745371`)
- **Tên đề tài đăng ký:**
  > Phát hiện và phân loại hành vi mã độc Botnet trên thiết bị IoT (Mirai, Hajime, Torii) sử dụng Machine Learning
- **Dataset sử dụng:**
  > Stratosphere IoT-23 Malware Dataset (Czech Technical University, 2020) — 5.696.295 bản ghi lưu lượng mạng Zeek Conn-Log (`https://www.stratosphereips.org/datasets-iot23`)
- **Mô hình & Công nghệ:**
  > Huấn luyện và đối sánh 5 thuật toán (Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM) theo chuẩn chia tách Stratified 80/20 (4.557.036 dòng Train / 1.139.259 dòng Test độc lập). Tích hợp mô hình LightGBM tối ưu (Accuracy 99.99%, F1-Score 99.99%, độ trễ suy luận batch 0.0043 ms/flow) vào Hệ thống Phòng vệ NIDS/IPS 3 bên (Attacker - AI NIDS Guardian - Victim IoT Device).

---

## PHẦN 2: KIẾN TRÚC DEMO GIẢ LẬP 3 BÊN (CHẠY TRÊN 1 LAPTOP HOẶC 2 LAPTOP QUA WI-FI/LAN)

Hệ thống được thiết kế theo mô hình **Simulation Testbed** linh hoạt, chuẩn hóa và an toàn trong phòng Lab. Các phân hệ được đánh số thống nhất:

| Phân hệ (Node) | File thực thi | Cổng mạng (Port) | Vai trò trong kịch bản Pentest & Phòng thủ |
| :--- | :--- | :--- | :--- |
| **Bên 1: Trạm Kẻ tấn công (Red Team Attacker Console)** | `live_demo/attacker_botnet_console.py` | Web UI: `9090` | Giao diện điều khiển chiến dịch Botnet (`http://127.0.0.1:9090`) cho phép phát động 4 kịch bản tấn công theo Kill-Chain (Mirai Scan, Brute-Force, Torii C&C, DDoS) hoặc chạy tự động bằng lệnh `--auto-demo`. |
| **Bên 2: Trạm Phòng vệ AI NIDS/IPS (Admin SOC Guardian)** | `live_demo/ai_nids_guardian_server.py` | SOC Dashboard: `5000` | Đóng vai trò Inline Gateway & Admin SOC (`http://127.0.0.1:5000`). Nạp mô hình `iot_nids_bundle.joblib` (LightGBM), trích xuất 12 đặc trưng Zeek flow trong `< 0.5 ms`, phân loại hành vi mã độc và hỗ trợ Admin bật **IPS Auto-Block** để khóa IP kẻ tấn công. |
| **Bên 3: Thiết bị IoT Nạn nhân (Victim IoT Device)** | `live_demo/victim_iot_server.py` | Web Portal: `8088`<br>Telnet Daemon: `2323` | Giả lập Camera thông minh `DUT-SmartCam-Pro-X1` có giao diện xem cảm biến cho người dùng (`http://127.0.0.1:8088`), mở cổng Telnet `2323` và định kỳ gửi lưu lượng sạch (Benign Telemetry) qua Gateway. |

---

## PHẦN 3: HƯỚNG DẪN KHỞI CHẠY NHANH TRƯỚC KHI LÊN BỤC BẢO VỆ

### Cách 1: Chạy toàn bộ 3 bên trên 1 Laptop (Khuyên dùng khi thuyết trình nhanh, ổn định 100%)
1. Nhấp đúp trực tiếp vào file:
   ```bat
   c:\Study\HocKy6\IoT_NIDS_Pipeline\start_demo_3_ben.bat
   ```
2. Script sẽ tự động bật 3 cửa sổ dịch vụ và mở sẵn 3 tab trình duyệt:
   - **Tab 1 (Admin SOC — Cổng 5000):** `http://127.0.0.1:5000`
   - **Tab 2 (Giao diện Người dùng Thiết bị IoT — Cổng 8088):** `http://127.0.0.1:8088`
   - **Tab 3 (Bảng điều khiển Kẻ tấn công Red Team — Cổng 9090):** `http://127.0.0.1:9090`

### Cách 2: Chạy phân tán trên 2 Laptop của 2 thành viên Nhóm 4 (Qua Wi-Fi/LAN)
Giả sử **Laptop 1 (Nguyễn Công Minh - Blue Team & IoT)** có địa chỉ IP Wi-Fi là `192.168.1.10` và **Laptop 2 (Ngô Văn Công - Red Team Attacker)** có địa chỉ IP Wi-Fi là `192.168.1.25`:

- **Trên Laptop 1 (Khởi chạy Trạm Gác AI NIDS + Thiết bị IoT Nạn nhân):**
  Mở 2 cửa sổ PowerShell tại thư mục `c:\Study\HocKy6\IoT_NIDS_Pipeline`:
  ```powershell
  # Cửa sổ 1: Khởi chạy AI NIDS Guardian lắng nghe trên toàn mạng LAN
  python live_demo/ai_nids_guardian_server.py --host 0.0.0.0 --port 5000 --victim-url http://127.0.0.1:8088

  # Cửa sổ 2: Khởi chạy Thiết bị IoT Nạn nhân
  python live_demo/victim_iot_server.py --host 0.0.0.0 --http-port 8088 --telnet-port 2323 --guardian-url http://127.0.0.1:5000
  ```

- **Trên Laptop 2 (Khởi chạy Bảng điều khiển Kẻ tấn công Red Team):**
  Mở PowerShell tại thư mục `c:\Study\HocKy6\IoT_NIDS_Pipeline`:
  ```powershell
  # Khởi chạy Red Team Attacker Console trỏ thẳng vào IP của Laptop 1
  python live_demo/attacker_botnet_console.py --host 0.0.0.0 --port 9090 --guardian-url http://192.168.1.10:5000 --victim-ip 192.168.1.10 --victim-telnet-port 2323
  ```
  Sau đó mở trình duyệt trên Laptop 2 tại `http://127.0.0.1:9090` để phát động tấn công. Màn hình SOC trên Laptop 1 (`http://192.168.1.10:5000`) sẽ lập tức nhận luồng, phân tích và kích hoạt IPS Auto-Block!

### LƯU Ý VỀ TÍNH CHẤT DEMO (SIMULATION TESTBED vs. RAW PACKET CAPTURE)
- Hệ thống demo được xây dựng theo mô hình **Simulation Testbed**: Module Attacker (`attacker_botnet_console.py`) mô phỏng luồng metadata chuẩn của 4 kịch bản Botnet Kill-Chain dưới dạng JSON và gửi qua REST API `/api/inspect_flow` của Trạm gác AI NIDS.
- Hệ thống demo **chưa tích hợp daemon bắt gói tin thô tầng kernel** (như libpcap hay Zeek realtime sniffing).
- Do đó, nếu kiểm thử viên dùng các công cụ Kali Linux (`nmap`, `hydra`, `hping3`) bắn trực tiếp vào địa chỉ IP của thiết bị:
  - Các gói tin mạng thực sự đi tới socket TCP của Victim (cổng Telnet 2323 phản hồi đăng nhập BusyBox, cổng Web 8088 nhận request).
  - Tuy nhiên, các gói tin thô đó không tự động chuyển thành JSON flow sang Guardian SOC nếu không qua agent thu thập.
- Khi thuyết trình, nhóm nêu rõ: Đây là kiến trúc **Simulation Testbed** phục vụ kiểm thử an toàn, có kiểm soát trong môi trường nghiên cứu; hướng phát triển thực tế tiếp theo là nhúng trực tiếp mô hình LightGBM lên phần cứng Gateway (OpenWrt / eBPF).

---

## PHẦN 4: KỊCH BẢN DEMO 4 BƯỚC TRÊN BỤC GIẢNG (THỜI LƯỢNG 3 - 5 PHÚT)

1. **Bước 1 — Trạng thái bình thường (Baseline Benign):**
   - Mở song song màn hình **Admin SOC (`:5000`)** bên trái và **Victim IoT Portal (`:8088`)** bên phải.
   - Bấm nút **"Gửi Telemetry hợp lệ ngay"** trên trang thiết bị IoT (`:8088`).
   - Chỉ cho giảng viên thấy trên bảng SOC (`:5000`): Dòng log hiển thị màu xanh lá `BENIGN (An toàn)` với giao thức `tcp / SF`, xác suất độc hại `0.0%`, trạng thái `ALLOWED`, và chỉ số CPU của thiết bị IoT duy trì ở mức ổn định (`~14%`).

2. **Bước 2 — Phát động chuỗi tấn công Botnet khi đang ở chế độ IDS Passive Alert:**
   - Đảm bảo nút trên thanh công cụ Admin SOC (`:5000`) đang ở trạng thái **`Chế độ: IDS (Chỉ cảnh báo)`**.
   - Chuyển sang tab **Red Team Attacker Console (`:9090`)**, lần lượt bấm:
     1. **1. Mirai Horizontal Port Scan** (gói tin `S0`, `orig_bytes=0`, thời gian kết nối cực ngắn).
     2. **2. Mirai Telnet Brute-Force** (dò mật khẩu dịch vụ `:2323`).
     3. **3. Torii C&C Beaconing** (kết nối máy chủ điều khiển cổng `4444/6667`).
     4. **4. Hajime/Mirai DDoS Flood** (bão gói tin SYN/UDP tốc độ cao).
   - Chỉ cho giảng viên thấy:
     - Mô hình LightGBM trên **Admin SOC (`:5000`)** lập tức phát hiện đúng 100% các luồng độc hại (`MALICIOUS`, xác suất `99.9% - 100.0%`), phân loại chính xác từng giai đoạn tấn công trong `< 0.5 ms`.
     - Tuy nhiên, vì đang ở chế độ **IDS (Chỉ cảnh báo)** nên các gói tin vẫn đi tới thiết bị IoT. Quay sang tab **Victim IoT (`:8088`)**, giảng viên sẽ thấy cảnh báo màu đỏ **"CẢNH BÁO: THIẾT BỊ ĐANG BỊ TẤN CÔNG BOTNET!"**, CPU thiết bị vọt lên `85% - 95%`.

3. **Bước 3 — Kích hoạt Phòng thủ Chủ động (Admin IPS Auto-Block):**
   - Trên giao diện **Admin SOC (`:5000`)**, bấm nút chuyển sang **`Chế độ: IPS Auto-Block (Đang bật)`** (hoặc bấm nút `Block IP` trực tiếp trên dòng cảnh báo).
   - Quay lại tab **Red Team Attacker (`:9090`)**, tiếp tục bấm tấn công **DDoS Flood** hoặc **Full Botnet Kill-Chain**.
   - Kết quả trực quan:
     - Tại **Red Team Console (`:9090`)**: Toàn bộ gói tin trả về trạng thái `BLOCKED_BY_IPS (HTTP 403)`.
     - Tại **Admin SOC (`:5000`)**: Cột hành động hiển thị nhãn `IPS_BLOCKED`, bộ đếm **Đã chặn bởi IPS** tăng lên, IP `192.168.56.105` nằm trong danh sách Firewall Blacklist.
     - Tại **Victim IoT (`:8088`)**: Lưu lượng tấn công bị cắt đứt hoàn toàn tại cổng Gateway, CPU thiết bị IoT hạ nhiệt về mức an toàn `14%`, trạng thái chuyển về **"ĐANG ĐƯỢC BẢO VỆ BỞI AI NIDS"**.

4. **Bước 4 — Trích xuất Báo cáo Kiểm toán SOC (Export Audit CSV):**
   - Trên màn hình **Admin SOC (`:5000`)**, bấm nút **`Xuất CSV Báo cáo`** để tải xuống file nhật ký sự cố phục vụ điều tra số (Digital Forensics).

---

## PHẦN 5: CÂU HỎI PHẢN BIỆN THƯỜNG GẶP & CÂU TRẢ LỜI MẪU CHO NHÓM 4

### Câu hỏi 1: Tại sao nhóm lại chia lại dữ liệu theo tỷ lệ 80/20 thay vì dùng nguyên file train/test cũ?
- **Trả lời:** Trong quá trình khảo sát dữ liệu (EDA), nhóm phát hiện cách chia cũ theo từng file kịch bản rời rạc khiến tập Train ban đầu hoàn toàn không có nhãn `Benign` (100% là Malicious), dẫn tới hiện tượng mô hình học vẹt (Zero-Variance / Data Leakage). Do đó, nhóm đã hợp nhất toàn bộ `5.696.295` bản ghi và thực hiện chia tách phân tầng (**Stratified Train-Test Split 80/20** với `random_state=42`):
  - **Tập Train (80%):** `4.557.036` bản ghi (`4.158.670` Malicious — `91.26%`, `398.366` Benign — `8.74%`).
  - **Tập Test độc lập (20%):** `1.139.259` bản ghi (`1.039.667` Malicious — `91.26%`, `99.592` Benign — `8.74%`).
  - Toàn bộ bộ mã hóa `OrdinalEncoder` và chuẩn hóa `StandardScaler` chỉ được `fit` trên tập Train và `transform` sang tập Test để triệt tiêu hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage).

### Câu hỏi 2: Tại sao nhóm chọn LightGBM để đóng gói vào hệ thống NIDS thời gian thực mà không chọn Random Forest hay Decision Tree?
- **Trả lời:** Khi thực nghiệm trên `4,55 triệu` dòng huấn luyện và kiểm thử trên `1,14 triệu` dòng độc lập:
  - Cả **LightGBM** và **Decision Tree** đều đạt độ chính xác `99.99%` (trên validation, Decision Tree F1 đạt 100.00% và LightGBM đạt 99.99%).
  - Tuy nhiên, một cây quyết định đơn lẻ (Decision Tree) rất dễ bị quá khớp (Overfitting) khi gặp biến thể gói tin mới ngoài thực tế. Trong khi đó, **LightGBM** là tập hợp chuỗi 100 cây Boosting (Histogram-based learning) với `max_depth=6`, vừa chống quá khớp nhờ học tăng cường, vừa có thời gian huấn luyện nhanh nhất (`19.83 giây` trên 4,55 triệu dòng — nhanh gấp `2.8 lần` Decision Tree `55.12s` và gấp `3.6 lần` Random Forest `71.61s`). Tốc độ suy luận trên tập Test 1,14 triệu dòng đạt `4.89 giây` (tương đương `0.0043 ms/luồng` ở chế độ batch), cực kỳ lý tưởng cho cổng Gateway IoT cấu hình thấp.

### Câu hỏi 3: Đặc trưng nào trong bộ dữ liệu IoT-23 đóng vai trò quan trọng nhất để phát hiện Botnet?
- **Trả lời:** Dựa trên phân tích Feature Importance từ bundle huấn luyện thật của mô hình LightGBM, 5 đặc trưng quan trọng nhất theo số lần phân tách nút (Split Count) là:
  1. `id.resp_p` (Cổng đích — `1380 splits`): Phản ánh trực tiếp mục tiêu dịch vụ nhạy cảm mà Botnet nhắm tới (như cổng Telnet `23/2323`, SSH `22`, HTTP `80/8080`, TR-069 `7547`, C&C `4444/6667`).
  2. `history` (Chuỗi lịch sử cờ TCP — `318 splits`): Ghi lại trình tự bắt tay TCP (`S`, `ShADadFr`, `Sr`), giúp phát hiện ngay các gói SYN bất thường trong các đòn quét bão táp.
  3. `id.orig_p` (Cổng nguồn — `289 splits`): Nhận diện quy luật sinh cổng nguồn tự động hoặc tuần tự trong mã nguồn công cụ quét của Botnet.
  4. `duration` (Thời lượng phiên — `281 splits`): Phân biệt các luồng quét tốc độ cao (`duration ~ 0`) với kết nối duy trì phiên C&C dài hạn (`Torii`).
  5. `orig_ip_bytes` (Tổng dung lượng byte IP từ nguồn — `229 splits`): Nhận diện lưu lượng phát tán gói tin đột biến từ mã độc.
