@echo off
echo ========================================================
echo   Menjalankan Aplikasi Procurement System (Flask Web)
echo ========================================================
echo.

IF EXIST "%~dp0venv\Scripts\python.exe" (
    echo Menggunakan Virtual Environment (venv)...
    "%~dp0venv\Scripts\python.exe" app.py
) ELSE IF EXIST "C:\laragon\bin\python\python-3.10\python.exe" (
    echo Menggunakan Python Laragon...
    "C:\laragon\bin\python\python-3.10\python.exe" app.py
) ELSE (
    echo Menggunakan Python default...
    python app.py
)

pause
