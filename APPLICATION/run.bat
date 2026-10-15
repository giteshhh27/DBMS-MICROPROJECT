@echo off
setlocal
cd /d "%~dp0"

TITLE College Library Management System
COLOR 0B

echo ===================================================================
echo     COLLEGE LIBRARY MANAGEMENT SYSTEM - CIRCULATION DESK
echo     MSBTE K Scheme - DMS 313302 Micro Project
echo ===================================================================
echo.

:: 1. Check Python installation
echo [1/3] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 goto python_error

python --version
echo [1/3] Python is ready.
echo.

:: 2. Check Database Connection
echo [2/3] Verifying MySQL database connection...
python -c "import sys, db; ok, msg = db.test_connection(); sys.exit(0 if ok else 1)" >nul 2>&1
if errorlevel 1 goto db_error

echo [2/3] MySQL Database connection: CONNECTED
echo.

:: 3. Launch browser and server
echo [3/3] Starting Library Circulation Desk on http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000

echo.
echo ===================================================================
echo   Circulation Desk running at: http://127.0.0.1:5000
echo.
echo   Staff Login Credentials:
echo     Username: admin
echo     Password: admin123
echo.
echo   [NOTE] Keep this window OPEN while using the library system.
echo   To stop the server, press Ctrl+C in this window.
echo ===================================================================
echo.

python app.py
goto end

:python_error
echo.
echo [ERROR] Python is not installed or not added to your Windows PATH.
echo Please install Python 3.8+ and ensure "Add Python to PATH" is checked.
echo.
pause
exit /b 1

:db_error
echo.
echo [ERROR] Could not connect to MySQL database!
echo.
echo Troubleshooting steps:
echo   1. Ensure MySQL Server service (MySQL80) is RUNNING.
echo      (Press Win+R, type services.msc, find MySQL80, click Start)
echo   2. Verify DB_PASSWORD in config.py matches your MySQL root password.
echo   3. Make sure database 'library_management' was loaded from
echo      'Library_Management_System.sql'.
echo.
pause
exit /b 1

:end
pause
