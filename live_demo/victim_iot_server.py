"""
BÊN 2 (NẠN NHÂN - VICTIM): HỆ THỐNG GIẢ LẬP THIẾT BỊ NHÀ THÔNG MINH IoT (SMART CAMERA & SENSOR GATEWAY)
Phục vụ Chương 3: Chức năng của người sử dụng (User) & Thiết bị IoT trong mô hình 3 bên.
- Cung cấp Giao diện Web cho người dùng cuối (User) xem trạng thái Camera/Cảm biến tại cổng 8088.
- Mở cổng dịch vụ mô phỏng Telnet IoT (2323) để nhận các kết nối quản trị từ xa.
- Tự động phát sinh lưu lượng cảm biến hợp lệ (Benign Telemetry) gửi qua Trạm gác AI NIDS (cổng 5000).
"""

import os
import sys
import time
import json
import random
import socket
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

GUARDIAN_URL = os.environ.get("GUARDIAN_URL", "http://127.0.0.1:5000")
VICTIM_HTTP_PORT = int(os.environ.get("VICTIM_HTTP_PORT", 8088))
VICTIM_TELNET_PORT = int(os.environ.get("VICTIM_TELNET_PORT", 2323))

# Trạng thái thiết bị IoT cho người dùng sử dụng
device_state = {
    "device_name": "DUT-SmartCam-Pro-X1",
    "firmware": "v2.4.8-arm64 (Linux Embedded)",
    "status": "ONLINE (Bình thường)",
    "camera_mode": "Đang ghi hình HD 1080p",
    "ir_night_vision": "Tự động (Auto)",
    "door_lock": "ĐÃ KHÓA (Locked)",
    "temperature": 26.5,
    "humidity": 62.0,
    "telemetry_sent": 0,
    "last_update": datetime.now().strftime("%H:%M:%S"),
    "access_logs": []
}


def forward_flow_to_guardian(flow_data):
    """Gửi thông tin luồng mạng sang Bên 3 (Trạm Gác AI NIDS) để phân tích và kiểm tra."""
    try:
        req = urllib.request.Request(
            f"{GUARDIAN_URL}/api/inspect_flow",
            data=json.dumps(flow_data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"action": "ALLOW", "prediction": "Benign", "confidence": "99.9%", "note": str(e)}


class IoTDeviceHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        client_ip = self.client_address[0]
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(device_state, ensure_ascii=False).encode("utf-8"))
            return

        # Gửi luồng truy cập Web của người sử dụng sang AI NIDS để kiểm tra
        flow = {
            "src_ip": client_ip,
            "src_port": random.randint(45000, 62000),
            "dst_ip": "192.168.1.50",
            "id.resp_p": VICTIM_HTTP_PORT,
            "proto": "tcp",
            "duration": round(random.uniform(0.05, 1.85), 3),
            "orig_bytes": random.randint(180, 520),
            "resp_bytes": random.randint(1200, 4500),
            "orig_pkts": random.randint(4, 10),
            "orig_ip_bytes": random.randint(380, 920),
            "resp_pkts": random.randint(5, 12),
            "resp_ip_bytes": random.randint(1500, 5100),
            "conn_state": "SF",
            "history": "ShADadFf",
            "attack_type_hint": "User Web Access (HTTP)"
        }
        verdict = forward_flow_to_guardian(flow)
        if verdict.get("action") == "BLOCK":
            self.send_response(403)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>403 FORBIDDEN - IP BLOCKED BY AI NIDS FIREWALL</h1>")
            return

        # Phục vụ giao diện Người sử dụng (User Dashboard của thiết bị IoT)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Smart Home IoT Portal - Giao Diện Người Sử Dụng</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        .header {{ background: #1e293b; padding: 20px 24px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #334155; }}
        .badge {{ background: #10b981; color: #052e16; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 13px; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }}
        .card h3 {{ margin-top: 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; }}
        .val {{ font-size: 26px; font-weight: 700; color: #38bdf8; margin: 8px 0; }}
        .btn {{ background: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: 600; margin-right: 10px; }}
        .btn:hover {{ background: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h2 style="margin:0;">📹 Thiết Bị IoT: {device_state['device_name']} (Giao diện Người Sử Dụng)</h2>
                <p style="margin:4px 0 0 0; color:#94a3b8; font-size:14px;">Firmware: {device_state['firmware']} | Cổng HTTP: {VICTIM_HTTP_PORT} | Cổng Telnet: {VICTIM_TELNET_PORT}</p>
            </div>
            <span class="badge">● ĐANG HOẠT ĐỘNG (PROTECTED BY AI NIDS)</span>
        </div>
        <div class="grid">
            <div class="card">
                <h3>Nhiệt độ & Độ ẩm cảm biến</h3>
                <div class="val" id="temp">{device_state['temperature']} °C / {device_state['humidity']}%</div>
                <p style="color:#64748b; font-size:13px;">Cập nhật lúc: <span id="time">{device_state['last_update']}</span></p>
            </div>
            <div class="card">
                <h3>Trạng thái Camera & Cửa</h3>
                <div class="val" style="color:#4ade80; font-size:20px;" id="lock">{device_state['door_lock']}</div>
                <p style="color:#94a3b8; font-size:13px;">Chế độ: {device_state['camera_mode']}</p>
            </div>
            <div class="card">
                <h3>Gói tin cảm biến đã gửi</h3>
                <div class="val" id="cnt">{device_state['telemetry_sent']}</div>
                <p style="color:#64748b; font-size:13px;">Giao thức: MQTT / HTTP / NTP (Benign)</p>
            </div>
        </div>
        <div class="card" style="margin-top:20px;">
            <h3>Điều khiển thiết bị của Người sử dụng (Tạo luồng mạng Benign thực tế)</h3>
            <button class="btn" onclick="sendNormalAction('sync_ntp')">🔄 Đồng bộ thời gian NTP (Port 123)</button>
            <button class="btn" onclick="sendNormalAction('send_mqtt')">📡 Gửi gói tin cảm biến MQTT (Port 1883)</button>
            <button class="btn" onclick="sendNormalAction('toggle_lock')">🔒 Đổi trạng thái Khóa cửa thông minh</button>
            <span id="msg" style="margin-left:12px; color:#4ade80; font-weight:600;"></span>
        </div>
    </div>
    <script>
        async function sendNormalAction(act) {{
            const res = await fetch('/api/user_action?act=' + act, {{method: 'POST'}});
            const data = await res.json();
            document.getElementById('msg').innerText = data.message;
            refreshStatus();
        }}
        async function refreshStatus() {{
            const res = await fetch('/api/status');
            const d = await res.json();
            document.getElementById('temp').innerText = d.temperature + ' °C / ' + d.humidity + '%';
            document.getElementById('lock').innerText = d.door_lock;
            document.getElementById('cnt').innerText = d.telemetry_sent;
            document.getElementById('time').innerText = d.last_update;
        }}
        setInterval(refreshStatus, 2000);
    </script>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        client_ip = self.client_address[0]
        if self.path.startswith("/api/user_action"):
            device_state["telemetry_sent"] += 1
            device_state["temperature"] = round(random.uniform(24.5, 28.5), 1)
            device_state["humidity"] = round(random.uniform(55.0, 68.0), 1)
            device_state["last_update"] = datetime.now().strftime("%H:%M:%S")
            if "toggle_lock" in self.path:
                device_state["door_lock"] = "ĐANG MỞ (Unlocked)" if "KHÓA" in device_state["door_lock"] else "ĐÃ KHÓA (Locked)"

            # Gửi luồng hợp lệ của người dùng sang AI NIDS
            flow = {
                "src_ip": client_ip,
                "src_port": random.randint(40000, 60000),
                "dst_ip": "192.168.1.50",
                "id.resp_p": 123 if "ntp" in self.path else (1883 if "mqtt" in self.path else 8088),
                "proto": "udp" if "ntp" in self.path else "tcp",
                "duration": round(random.uniform(0.12, 2.40), 3),
                "orig_bytes": random.randint(90, 260),
                "resp_bytes": random.randint(120, 480),
                "orig_pkts": random.randint(2, 6),
                "orig_ip_bytes": random.randint(150, 420),
                "resp_pkts": random.randint(2, 6),
                "resp_ip_bytes": random.randint(180, 600),
                "conn_state": "SF",
                "history": "ShADadFf" if "ntp" not in self.path else "Dd",
                "attack_type_hint": "Benign User IoT Command"
            }
            verdict = forward_flow_to_guardian(flow)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "message": f"Đã thực thi lệnh! AI NIDS đánh giá: {verdict.get('prediction')} ({verdict.get('confidence')})"
            }, ensure_ascii=False).encode("utf-8"))


def run_telnet_honeypot():
    """Giả lập cổng Telnet 2323 trên thiết bị IoT để nhận kết nối từ xa hoặc bị Botnet Mirai tấn công."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", VICTIM_TELNET_PORT))
        srv.listen(20)
        print(f"[+] [VICTIM IoT] Dịch vụ Telnet IoT đang mở tại cổng {VICTIM_TELNET_PORT}")
        while True:
            conn, addr = srv.accept()
            try:
                conn.settimeout(1.5)
                conn.sendall(b"DUT-SmartCam-Pro-X1 Login: ")
                data = conn.recv(256)
                conn.sendall(b"Password: ")
            except Exception:
                pass
            finally:
                conn.close()
    except Exception as e:
        print(f"[!] Lỗi cổng Telnet giả lập: {e}")


def auto_telemetry_loop():
    """Tự động gửi các bản tin cảm biến sạch (Benign) định kỳ mỗi 4 giây."""
    while True:
        time.sleep(4.0)
        device_state["telemetry_sent"] += 1
        device_state["temperature"] = round(random.uniform(25.0, 27.8), 1)
        device_state["last_update"] = datetime.now().strftime("%H:%M:%S")
        flow = {
            "src_ip": "192.168.1.50 (IoT-Cam)",
            "src_port": random.randint(35000, 58000),
            "dst_ip": "8.8.8.8 (Cloud-Server)",
            "id.resp_p": random.choice([443, 123, 53, 8088]),
            "proto": random.choice(["tcp", "udp"]),
            "duration": round(random.uniform(0.08, 3.20), 3),
            "orig_bytes": random.randint(64, 320),
            "resp_bytes": random.randint(128, 640),
            "orig_pkts": random.randint(2, 8),
            "orig_ip_bytes": random.randint(120, 520),
            "resp_pkts": random.randint(2, 8),
            "resp_ip_bytes": random.randint(180, 820),
            "conn_state": "SF",
            "history": "ShADadFf",
            "attack_type_hint": "Benign IoT Sensor Telemetry"
        }
        forward_flow_to_guardian(flow)


if __name__ == "__main__":
    print("=" * 70)
    print(" KHỞI ĐỘNG BÊN 2: THIẾT BỊ IoT NẠN NHÂN (SMART CAMERA & SENSOR)")
    print(f" - Giao diện Người sử dụng (Web): http://127.0.0.1:{VICTIM_HTTP_PORT}")
    print(f" - Cổng dịch vụ Telnet IoT      : Port {VICTIM_TELNET_PORT}")
    print("=" * 70)
    threading.Thread(target=run_telnet_honeypot, daemon=True).start()
    threading.Thread(target=auto_telemetry_loop, daemon=True).start()
    server = HTTPServer(("0.0.0.0", VICTIM_HTTP_PORT), IoTDeviceHTTPHandler)
    server.serve_forever()

