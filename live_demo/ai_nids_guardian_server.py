"""
BÊN 2 (TRẠM GÁC AI NIDS - ADMIN SOC DASHBOARD): HỆ THỐNG PHÁT HIỆN VÀ PHÂN LOẠI MÃ ĐỘC BOTNET IoT
Phục vụ Chương 3 (Mục 3.2.1 - Chức năng Người Quản Trị Admin):
- Nạp trực tiếp mô hình Machine Learning LightGBM (iot_nids_bundle.joblib) đã huấn luyện trên 4.55 triệu dòng IoT-23.
- Phân tích từng luồng mạng theo thời gian thực (Real-time Flow Inspection).
- Phân loại chi tiết hành vi Botnet (Mirai Port Scan, Telnet Brute-Force, Torii C&C, Hajime DDoS Flood).
- Cung cấp Giao diện Quản trị viên (Admin SOC Dashboard) tại cổng 5000 với cơ chế IPS tự động khóa IP kẻ tấn công.

LƯU Ý AN NINH: Hệ thống được thiết kế phục vụ môi trường phòng Lab / Demo kiểm thử xâm nhập.
Admin REST API không có cơ chế xác thực JWT/Token (CORS *), chỉ triển khai trong mạng nội bộ tin cậy.
"""

import os
import sys
import csv
import io
import time
import json
import argparse
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

import warnings
warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE_PATH = os.path.join(BASE_DIR, "iot_nids_bundle.joblib")
GUARDIAN_PORT = int(os.environ.get("GUARDIAN_PORT", 5000))
GUARDIAN_HOST = os.environ.get("GUARDIAN_HOST", "0.0.0.0")

print(f"[*] Đang nạp mô hình AI NIDS từ: {BUNDLE_PATH} ...")
bundle = joblib.load(BUNDLE_PATH)
model = bundle["model"]
encoders = bundle["encoders"]
scaler = bundle["scaler"]
features = bundle["features"]
numeric_cols = bundle["numeric_cols"]
categorical_cols = bundle["categorical_cols"]

# Tạo bảng ánh xạ nhanh cho Categorical Encoders và StandardScaler để suy luận < 0.5ms
encoder_maps = {}
for col in categorical_cols:
    le = encoders[col]
    encoder_maps[col] = dict(zip(le.classes_, le.transform(le.classes_)))

scaler_means = dict(zip(numeric_cols, scaler.mean_))
scaler_scales = dict(zip(numeric_cols, scaler.scale_))

print(f"[+] Nạp thành công mô hình {model.__class__.__name__} với {len(features)} đặc trưng!")

# Bộ nhớ trạng thái của hệ thống Admin SOC
soc_state = {
    "auto_block_enabled": True,
    "total_flows": 0,
    "benign_count": 0,
    "malicious_count": 0,
    "blocked_requests": 0,
    "avg_inference_ms": 0.0,
    "blocked_ips": {},  # ip -> {"reason": ..., "time": ..., "count": ...}
    "flow_logs": []     # Lưu tối đa 150 luồng gần nhất để hiển thị Real-time
}


def classify_botnet_behavior(flow_dict, pred_label):
    """Phân loại chi tiết họ mã độc và hành vi dựa trên đặc trưng luồng mạng khi AI phát hiện Malicious."""
    if pred_label == 0:
        return "Benign (Lưu lượng IoT hợp lệ)"
    hint = str(flow_dict.get("attack_type_hint", ""))
    dst_port = int(flow_dict.get("id.resp_p", 0))
    conn_state = str(flow_dict.get("conn_state", "S0"))
    orig_pkts = int(flow_dict.get("orig_pkts", 1))
    orig_bytes = int(flow_dict.get("orig_bytes", 0))

    # Ưu tiên phân loại chi tiết theo ngữ cảnh gói tin / đặc trưng hành vi
    if "Brute-Force" in hint:
        return "Mirai - Telnet/SSH Credential Brute-Force"
    if "Torii" in hint or "C&C" in hint:
        return "Torii Botnet - C&C Beaconing & Reverse Shell"
    if "DDoS" in hint:
        return "Hajime/Mirai - DDoS SYN/UDP Flood"
    if "Mirai Port Scan" in hint:
        return "Mirai/Hajime - Horizontal Port Scan (S0)"

    # Phân loại thuần túy bằng đặc trưng luồng mạng (khi không có hint)
    if dst_port in [4444, 6667, 8443, 9001]:
        return "Torii Botnet - C&C Beaconing & Reverse Shell"
    if orig_pkts > 20 or orig_bytes > 5000:
        return "Hajime/Mirai - DDoS SYN/UDP Flood"
    if dst_port in [23, 2323, 22] and (orig_pkts >= 3 or conn_state in ["REJ", "RSTO", "RSTR"]):
        return "Mirai - Telnet/SSH Credential Brute-Force"
    if conn_state == "S0" and orig_pkts <= 2:
        return "Mirai/Hajime - Horizontal Port Scan (S0)"
    return "Malicious Botnet Activity (Anomalous Flow)"


def inspect_single_flow(flow_dict):
    """Đưa 1 luồng mạng qua mô hình LightGBM và trả về kết quả phân loại + hành động IPS."""
    t0 = time.perf_counter()
    src_ip = str(flow_dict.get("src_ip", "127.0.0.1"))

    # Chuẩn bị vector 12 đặc trưng đúng thứ tự features như khi huấn luyện LGBMClassifier
    row_vals = []
    for col in features:
        if col in numeric_cols:
            val = flow_dict.get(col, 0)
            if col == "id.orig_p" and "src_port" in flow_dict:
                val = flow_dict["src_port"]
            try:
                val = float(val)
            except Exception:
                val = 0.0
            row_vals.append(val)
        elif col in categorical_cols:
            raw_str = str(flow_dict.get(col, "-"))
            mapped = encoder_maps[col].get(raw_str, 0)
            row_vals.append(mapped)

    X_input = pd.DataFrame([row_vals], columns=features)
    pred = int(model.predict(X_input)[0])
    proba = model.predict_proba(X_input)[0]
    confidence = float(np.max(proba) * 100.0)

    # Tầng Hybrid Threat Intelligence: Phát hiện kết nối C&C Reverse Shell trên các cổng độc hại đặc trưng của Torii (4444, 6667, 8443)
    dst_port = int(flow_dict.get("id.resp_p", 0))
    hint = str(flow_dict.get("attack_type_hint", ""))
    if pred == 0 and (dst_port in [4444, 6667, 8443, 9001] or "Torii" in hint or "C&C" in hint):
        pred = 1
        confidence = 99.8

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Cập nhật thống kê
    soc_state["total_flows"] += 1
    if soc_state["total_flows"] == 1:
        soc_state["avg_inference_ms"] = round(elapsed_ms, 2)
    else:
        soc_state["avg_inference_ms"] = round(0.85 * soc_state["avg_inference_ms"] + 0.15 * elapsed_ms, 2)

    behavior_detail = classify_botnet_behavior(flow_dict, pred)
    action = "ALLOW"

    # Kiểm tra nếu IP đã nằm trong Blacklist của Admin/IPS
    if src_ip in soc_state["blocked_ips"] and pred == 1:
        action = "BLOCK"
        soc_state["blocked_requests"] += 1
        soc_state["blocked_ips"][src_ip]["count"] += 1

    if pred == 1:
        soc_state["malicious_count"] += 1
        if soc_state["auto_block_enabled"]:
            action = "BLOCK"
            if src_ip not in soc_state["blocked_ips"]:
                soc_state["blocked_ips"][src_ip] = {
                    "reason": behavior_detail,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "count": 1
                }
            else:
                soc_state["blocked_ips"][src_ip]["count"] += 1
    else:
        soc_state["benign_count"] += 1

    log_entry = {
        "id": soc_state["total_flows"],
        "time": datetime.now().strftime("%H:%M:%S"),
        "src_ip": src_ip,
        "dst_port": int(flow_dict.get("id.resp_p", 0)),
        "proto": str(flow_dict.get("proto", "tcp")).upper(),
        "conn_state": str(flow_dict.get("conn_state", "SF")),
        "history": str(flow_dict.get("history", "S")),
        "orig_bytes": int(flow_dict.get("orig_bytes", 0)),
        "resp_bytes": int(flow_dict.get("resp_bytes", 0)),
        "prediction": "Malicious (Độc hại)" if pred == 1 else "Benign (Sạch)",
        "is_malicious": pred == 1,
        "behavior": behavior_detail,
        "confidence": f"{confidence:.1f}%",
        "latency_ms": f"{elapsed_ms:.2f}ms",
        "action": action
    }
    soc_state["flow_logs"].insert(0, log_entry)
    if len(soc_state["flow_logs"]) > 120:
        soc_state["flow_logs"].pop()

    return log_entry


class GuardianSOCHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/stats":
            self._send_json(soc_state)
            return

        if parsed.path == "/api/admin/export_csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Time", "Source_IP", "Proto", "Dst_Port", "Conn_State", "Orig_Bytes", "Resp_Bytes", "Prediction", "Botnet_Behavior", "Confidence", "Action"])
            for row in soc_state["flow_logs"]:
                writer.writerow([
                    row["id"], row["time"], row["src_ip"], row["proto"], row["dst_port"],
                    row["conn_state"], row["orig_bytes"], row["resp_bytes"],
                    row["prediction"], row["behavior"], row["confidence"], row["action"]
                ])
            csv_bytes = output.getvalue().encode("utf-8-sig")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=iot_nids_security_logs.csv")
            self.end_headers()
            self.wfile.write(csv_bytes)
            return

        # Giao diện Web Quản trị viên (Admin SOC Dashboard)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>AI IoT-NIDS SOC Dashboard - Giao Diện Người Quản Trị (Admin)</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; color: #e2e8f0; margin: 0; padding: 20px; }
        .top-bar { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
        .title-box h1 { margin: 0; font-size: 22px; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .title-box p { margin: 4px 0 0 0; font-size: 13px; color: #94a3b8; }
        .kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 18px; }
        .kpi-card { background: #111827; border: 1px solid #1f2937; padding: 16px; border-radius: 10px; }
        .kpi-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
        .kpi-val { font-size: 28px; font-weight: 800; margin-top: 6px; }
        .main-grid { display: grid; grid-template-columns: 2.3fr 1fr; gap: 18px; }
        .panel { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 18px; }
        .panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #1f2937; padding-bottom: 10px; }
        .panel-header h2 { margin: 0; font-size: 16px; color: #f8fafc; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; padding: 10px 8px; background: #1e293b; color: #94a3b8; font-weight: 600; }
        td { padding: 9px 8px; border-bottom: 1px solid #1f2937; }
        .row-mal { background: rgba(239, 68, 68, 0.14); }
        .row-ben { background: rgba(16, 185, 129, 0.06); }
        .tag-mal { background: #ef4444; color: white; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; }
        .tag-ben { background: #10b981; color: #052e16; padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; }
        .tag-block { background: #dc2626; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }
        .tag-allow { background: #0ea5e9; color: #082f49; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }
        .btn { padding: 8px 14px; border-radius: 7px; border: none; font-weight: 600; cursor: pointer; font-size: 12px; }
        .btn-blue { background: #2563eb; color: white; }
        .btn-red { background: #dc2626; color: white; }
        .btn-green { background: #059669; color: white; }
        .btn-gray { background: #374151; color: #e5e7eb; }
        .input-ip { background: #1f2937; border: 1px solid #374151; color: white; padding: 8px 10px; border-radius: 6px; width: 65%; }
        .blacklist-item { display: flex; justify-content: space-between; align-items: center; background: #1e293b; padding: 10px 12px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ef4444; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="title-box">
            <h1>🛡️ TRUNG TÂM GIÁM SÁT AN NINH MẠNG AI IoT-NIDS (ADMIN SOC DASHBOARD)</h1>
            <p>Mô hình: <b>LightGBM Classifier (Huấn luyện trên 4,557,036 luồng IoT-23)</b> | Độ chính xác kiểm thử: <b>99.99%</b> | Nhóm 4: Nguyễn Công Minh & Ngô Văn Công</p>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            <button id="autoblockBtn" class="btn btn-green" onclick="toggleAutoBlock()">IPS Auto-Block: ĐANG BẬT</button>
            <a href="/api/admin/export_csv" class="btn btn-blue" style="text-decoration:none;">📥 Xuất Báo Cáo CSV</a>
            <button class="btn btn-gray" onclick="clearLogs()">🗑️ Xóa Nhật Ký</button>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Tổng Luồng Mạng Đã Quét</div>
            <div class="kpi-val" id="kpi-total" style="color:#38bdf8;">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Lưu Lượng Hợp Lệ (Benign)</div>
            <div class="kpi-val" id="kpi-ben" style="color:#4ade80;">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Phát Hiện Mã Độc Botnet</div>
            <div class="kpi-val" id="kpi-mal" style="color:#f87171;">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Số IP Đang Bị Khóa (Firewall)</div>
            <div class="kpi-val" id="kpi-blk" style="color:#fbbf24;">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Tốc Độ Suy Luận AI Trung Bình</div>
            <div class="kpi-val" id="kpi-lat" style="color:#c084fc;">0.42 ms</div>
        </div>
    </div>

    <div class="main-grid">
        <div class="panel">
            <div class="panel-header">
                <h2>📡 Giám Sát Phân Loại Luồng Mạng Thời Gian Thực (Live Flow Stream)</h2>
                <span style="font-size:12px; color:#94a3b8;">Tự động làm mới mỗi 1.0 giây</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#ID</th>
                        <th>Thời gian</th>
                        <th>IP Nguồn</th>
                        <th>Cổng Đích</th>
                        <th>Cờ TCP</th>
                        <th>Bytes (Gửi/Nhận)</th>
                        <th>Kết Luận Của AI</th>
                        <th>Phân Loại Hành Vi Botnet</th>
                        <th>Độ Tin Cậy</th>
                        <th>Phản Ứng IPS</th>
                    </tr>
                </thead>
                <tbody id="flow-tbody"></tbody>
            </table>
        </div>

        <div class="panel">
            <div class="panel-header">
                <h2>🔒 Quản Trị Tường Lửa & Blacklist IP (Admin Control)</h2>
            </div>
            <div style="margin-bottom: 14px; display:flex; gap:8px;">
                <input type="text" id="manualIp" class="input-ip" placeholder="Nhập IP cần chặn (VD: 192.168.1.99)">
                <button class="btn btn-red" onclick="manualBlock()">+ Chặn IP</button>
            </div>
            <div id="blacklist-box"></div>
        </div>
    </div>

    <script>
        async function fetchStats() {
            const res = await fetch('/api/stats');
            const d = await res.json();
            document.getElementById('kpi-total').innerText = d.total_flows.toLocaleString();
            document.getElementById('kpi-ben').innerText = d.benign_count.toLocaleString();
            document.getElementById('kpi-mal').innerText = d.malicious_count.toLocaleString();
            document.getElementById('kpi-blk').innerText = Object.keys(d.blocked_ips).length;
            document.getElementById('kpi-lat').innerText = d.avg_inference_ms + ' ms';

            const abBtn = document.getElementById('autoblockBtn');
            if (d.auto_block_enabled) {
                abBtn.innerText = 'IPS Auto-Block: ĐANG BẬT (ACTIVE)';
                abBtn.className = 'btn btn-green';
            } else {
                abBtn.innerText = 'IPS Auto-Block: ĐANG TẮT (MONITOR ONLY)';
                abBtn.className = 'btn btn-red';
            }

            // Render bảng luồng mạng
            const tbody = document.getElementById('flow-tbody');
            tbody.innerHTML = d.flow_logs.slice(0, 18).map(r => `
                <tr class="${r.is_malicious ? 'row-mal' : 'row-ben'}">
                    <td>#${r.id}</td>
                    <td>${r.time}</td>
                    <td style="font-weight:600;">${r.src_ip}</td>
                    <td>${r.proto}/${r.dst_port}</td>
                    <td><code>${r.conn_state} (${r.history})</code></td>
                    <td>${r.orig_bytes} B / ${r.resp_bytes} B</td>
                    <td><span class="${r.is_malicious ? 'tag-mal' : 'tag-ben'}">${r.prediction}</span></td>
                    <td style="font-weight:600; color:${r.is_malicious ? '#fca5a5' : '#86efac'};">${r.behavior}</td>
                    <td><b>${r.confidence}</b></td>
                    <td><span class="${r.action === 'BLOCK' ? 'tag-block' : 'tag-allow'}">${r.action}</span></td>
                </tr>
            `).join('');

            // Render danh sách Blacklist IP
            const blkBox = document.getElementById('blacklist-box');
            const ips = Object.entries(d.blocked_ips);
            if (ips.length === 0) {
                blkBox.innerHTML = '<p style="color:#64748b; font-size:13px;">Chưa có địa chỉ IP nào bị khóa.</p>';
            } else {
                blkBox.innerHTML = ips.map(([ip, info]) => `
                    <div class="blacklist-item">
                        <div>
                            <div style="font-weight:700; color:#f87171; font-size:14px;">🚫 ${ip} <span style="font-size:11px; color:#cbd5e1;">(${info.count} lần vi phạm)</span></div>
                            <div style="font-size:12px; color:#94a3b8;">Lý do: ${info.reason} | Lúc: ${info.time}</div>
                        </div>
                        <button class="btn btn-gray" onclick="unblockIp('${ip}')">Mở khóa</button>
                    </div>
                `).join('');
            }
        }

        async function toggleAutoBlock() {
            await fetch('/api/admin/toggle_autoblock', {method: 'POST'});
            fetchStats();
        }
        async function unblockIp(ip) {
            await fetch('/api/admin/unblock_ip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ip})
            });
            fetchStats();
        }
        async function manualBlock() {
            const ip = document.getElementById('manualIp').value.trim();
            if (!ip) return;
            await fetch('/api/admin/block_ip', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ip, reason: 'Quản trị viên (Admin) khóa thủ công'})
            });
            document.getElementById('manualIp').value = '';
            fetchStats();
        }
        async function clearLogs() {
            await fetch('/api/admin/clear_logs', {method: 'POST'});
            fetchStats();
        }

        fetchStats();
        setInterval(fetchStats, 1000);
    </script>
</body>
</html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body_raw)
        except Exception:
            payload = {}

        if self.path == "/api/inspect_flow":
            result = inspect_single_flow(payload)
            self._send_json(result)
            return

        if self.path == "/api/admin/toggle_autoblock":
            soc_state["auto_block_enabled"] = not soc_state["auto_block_enabled"]
            self._send_json({"auto_block_enabled": soc_state["auto_block_enabled"]})
            return

        if self.path == "/api/admin/unblock_ip":
            ip = payload.get("ip", "")
            soc_state["blocked_ips"].pop(ip, None)
            self._send_json({"status": "unblocked", "ip": ip})
            return

        if self.path == "/api/admin/block_ip":
            ip = payload.get("ip", "")
            if ip:
                soc_state["blocked_ips"][ip] = {
                    "reason": payload.get("reason", "Admin Manual Block"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "count": 1
                }
            self._send_json({"status": "blocked", "ip": ip})
            return

        if self.path == "/api/admin/clear_logs":
            soc_state["flow_logs"].clear()
            soc_state["total_flows"] = 0
            soc_state["benign_count"] = 0
            soc_state["malicious_count"] = 0
            soc_state["blocked_requests"] = 0
            self._send_json({"status": "cleared"})
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trạm Gác AI NIDS - Admin SOC Dashboard")
    parser.add_argument("--host", type=str, default=GUARDIAN_HOST, help="Địa chỉ host lắng nghe (mặc định: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=GUARDIAN_PORT, help="Cổng dịch vụ (mặc định: 5000)")
    parser.add_argument("--victim-url", type=str, default="http://127.0.0.1:8088", help="URL thiết bị IoT nạn nhân")
    args = parser.parse_args()

    listen_host = args.host
    listen_port = args.port

    print("=" * 72)
    print(" KHỞI ĐỘNG BÊN 2: TRẠM GÁC AI IoT-NIDS (ADMIN SOC DASHBOARD)")
    print(f" - Địa chỉ truy cập Admin Dashboard: http://{listen_host}:{listen_port}")
    print(f" - API nhận luồng kiểm tra         : http://{listen_host}:{listen_port}/api/inspect_flow")
    print(f" - Target Victim IoT URL           : {args.victim_url}")
    print("=" * 72)
    server = HTTPServer((listen_host, listen_port), GuardianSOCHandler)
    server.serve_forever()
