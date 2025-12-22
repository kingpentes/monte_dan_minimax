@echo off
echo ========================================
echo Git Commit and Push Helper
echo ========================================
echo.

REM Check for changes
git status --short
if errorlevel 1 (
    echo [ERROR] Bukan repository Git!
    pause
    exit /b 1
)

echo.
echo File yang akan di-commit:
git status --short
echo.

REM Get commit message
set /p MESSAGE="Masukkan commit message: "
if "%MESSAGE%"=="" (
    set MESSAGE=Update project untuk Vercel deployment
)

echo.
echo [INFO] Commit message: %MESSAGE%
echo.

REM Git operations
echo [INFO] Adding files...
git add .

echo [INFO] Committing...
git commit -m "%MESSAGE%"
if errorlevel 1 (
    echo [WARNING] Tidak ada perubahan untuk di-commit atau commit gagal
)

echo.
set /p PUSH="Push ke GitHub? (y/n): "
if /i "%PUSH%"=="y" (
    echo [INFO] Pushing to remote...
    git push
    if errorlevel 1 (
        echo [ERROR] Push gagal! Cek koneksi atau remote repository.
    ) else (
        echo [OK] Berhasil push ke GitHub!
        echo.
        echo ========================================
        echo Next: Deploy ke Vercel
        echo ========================================
        echo 1. Login ke https://vercel.com
        echo 2. Import project dari GitHub
        echo 3. Deploy!
        echo ========================================
    )
) else (
    echo [INFO] Skipped push. Jalankan 'git push' manual jika diperlukan.
)

echo.
pause
