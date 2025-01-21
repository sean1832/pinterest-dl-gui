@echo off
REM Update from git repository. You need to have git installed.
echo Updating from repository...

FOR /F "tokens=*" %%i IN ('git pull') DO (
    echo %%i
    echo %%i | findstr /C:"Already up to date." >nul
    IF NOT ERRORLEVEL 1 (
        echo Exiting...
        pause
        exit /b
    )
)

echo Initializing virtual environment...
CALL venv\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b
)

echo Update complete.
pause
