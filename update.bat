@echo off
REM ======================================================
REM Updated Script to Update Python Project from Git Repo
REM ======================================================

echo Updating from repository...

REM Capture git pull output to a temporary file including errors
git pull > gitpull.log 2>&1
IF ERRORLEVEL 1 (
    echo Error: Failed to pull changes. Check gitpull.log for details.
    type gitpull.log
    pause
    exit /b
)

REM Check if repository is already up to date
findstr /C:"Already up to date." gitpull.log >nul
IF %ERRORLEVEL% EQU 0 (
    echo Repository is already up to date. Exiting...
    del gitpull.log
    pause
    exit /b
)

REM Clean up temporary file after successful update
del gitpull.log
echo Repository updated successfully.

REM Check if the virtual environment activation script exists
IF NOT EXIST venv\Scripts\activate.bat (
    echo Error: Virtual environment not found at "venv\Scripts\activate.bat".
    pause
    exit /b
)

echo Initializing virtual environment...
CALL venv\Scripts\activate.bat

REM Verify existence of requirements.txt
IF NOT EXIST requirements.txt (
    echo Error: requirements.txt not found.
    pause
    exit /b
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b
)

echo Update complete.
pause
