@echo off
echo ========================================
echo Chess Engine Web - Local Test Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu.
    pause
    exit /b 1
)

echo [OK] Python ditemukan
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Membuat virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Gagal membuat virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment berhasil dibuat
    echo.
)

REM Activate virtual environment
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Gagal mengaktifkan virtual environment!
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Menginstall dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Gagal install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies terinstall
echo.

REM Run the app
echo ========================================
echo [INFO] Menjalankan server...
echo [INFO] Akses di: http://localhost:5000
echo [INFO] Tekan Ctrl+C untuk stop server
echo ========================================
echo.

python web\app.py

pause
