@echo off
title GM AI Core Matrix Orchestrator
cls
echo ======================================================
echo       GM AI v1.7 -- CROSS-DEVICE AGENT WORKSPACE      
echo ======================================================
echo [*] Status: Initializing deep framework modules...
echo [*] Directory: %CD%

if not exist gm_memory.db (
    echo [!] Warning: Relational memory state ledger missing. Building local instance...
)

echo [*] Target: Serving Local Web UI Dashboard on port 8000...
start "GM AI Web Server Dashboard" cmd /k "python -m http.server 8000 --directory storage\dashboard"

echo [*] Target: Starting secure background network telemetry brokers...
start "GM AI Network Broker Server" cmd /k "python src\communication\socket_broker.py"

echo [*] Target: Initializing automated background telemetry task schedulers...
start "GM AI Telemetry Task Daemon" cmd /k "python src\execution\task_scheduler.py"

echo [*] Target: Initializing primary human interactive console environment...
echo ======================================================
echo [SYSTEM ONLINE] Waiting for remote or local state triggers.
echo Web UI Portal available at: http://localhost:8000
echo ======================================================
echo.
cmd /k "python app.py"
