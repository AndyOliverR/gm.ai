@echo off
TITLE GM AI Engine Launcher
CLS
echo ====================================================
echo   GM AI Core System Workspace Launcher Initializing
echo ====================================================
echo.

:: Step 1: Verify if Ollama endpoint process is already responsive
echo [STEP 1/3] Verifying background server node...
curl -s http://127.0.0 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Active Ollama engine detected. Proceeding...
) else (
    echo [WARN] Ollama engine is offline. Attempting to start daemon process...
    start /min "Ollama Daemon Server" ollama serve
    echo Waiting for server socket connection to initialize...
    timeout /t 5 /nobreak >nul
)

:: Step 2: Run core regression integration testing metrics
echo.
echo [STEP 2/3] Executing core module verification tests...
python -m unittest discover -s C:\gm.ai\tests -p "test_*.py" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Core tests passed successfully. Integrity confirmed.
) else (
    echo [WARN] Local regression tests registered a warning. Proceeding to sandbox...
)

:: Step 3: Run interactive terminal workspace console
echo.
echo [STEP 3/3] Mounting interactive control node environment...
echo.
cd /d C:\gm.ai
python test_interactive_node.py

echo.
echo ====================================================
echo   GM AI Workspace Session Closed Safely. Exiting...
echo ====================================================
pause
