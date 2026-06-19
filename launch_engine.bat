@echo off
title GM AI Core Matrix Orchestrator
cls
echo ======================================================
echo       GM AI v1.5 -- CROSS-DEVICE AGENT WORKSPACE      
echo ======================================================
echo [*] Status: Initializing deep framework modules...
echo [*] Directory: %CD%

:: Validate underlying project configuration presence
if not exist gm_memory.db (
    echo [!] Warning: Relational memory state ledger missing. Building local instance...
)

echo [*] Target: Starting secure background network telemetry brokers...
:: Launch the audited WebSocket server pipeline inside a secondary concurrent shell
start "GM AI Network Broker Server" cmd /k "python src\communication\socket_broker.py"

echo [*] Target: Initializing primary human interactive console environment...
echo ======================================================
echo [SYSTEM ONLINE] Waiting for remote or local state triggers.
echo To read current historical timeline entries, execute:
echo   python src\execution\audit_ledger.py
echo ======================================================
echo.
cmd /k "python app.py"
