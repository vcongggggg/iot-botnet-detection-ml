@echo off
chcp 65001 >nul
title HE THONG DEMO 3 BEN: ATTACKER - AI IoT-NIDS - VICTIM IoT
echo ============================================================================
echo   KHOI DONG MO HINH THUC NGHIEM 3 BEN (IOT BOTNET DETECTION - NHOM 4)
echo   1. Ben 3 (Tram Gac AI NIDS - Admin SOC) : http://127.0.0.1:5000
echo   2. Ben 2 (Thiet bi IoT Nan nhan - User) : http://127.0.0.1:8088
echo   3. Ben 1 (Ke tan cong Red Team Botnet)  : http://127.0.0.1:9090
echo ============================================================================

start "BEN 3 - AI NIDS ADMIN SOC (Port 5000)" cmd /k "python "%~dp0live_demo\ai_nids_guardian_server.py""
timeout /t 3 >nul
start "BEN 2 - VICTIM IoT DEVICE (Port 8088)" cmd /k "python "%~dp0live_demo\victim_iot_server.py""
timeout /t 2 >nul
start "BEN 1 - RED TEAM BOTNET CONSOLE (Port 9090)" cmd /k "python "%~dp0live_demo\attacker_botnet_console.py""
timeout /t 2 >nul

start http://127.0.0.1:5000
start http://127.0.0.1:8088
start http://127.0.0.1:9090

echo [+] Da khoi dong thanh cong ca 3 ben va mo giao dien tren trinh duyet!
pause

