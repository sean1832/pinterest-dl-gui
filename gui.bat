@echo off
REM Check if the venv directory exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b
    )
    echo Virtual environment created.

    REM Activate the virtual environment
    CALL venv\Scripts\activate.bat
    IF ERRORLEVEL 1 (
        echo Error: Failed to activate virtual environment.
        pause
        exit /b
    )

    REM Install requirements from requirements.txt
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo Error: Failed to install dependencies.
        pause
        exit /b
    )
    echo Dependencies installed.
) ELSE (
    REM Activate the virtual environment
    CALL venv\Scripts\activate.bat
    IF ERRORLEVEL 1 (
        echo Error: Failed to activate virtual environment.
        pause
        exit /b
    )
)

REM Start the GUI
echo Starting GUI...
streamlit run gui.py
IF ERRORLEVEL 1 (
    echo Error: Failed to start the GUI.
    pause
    exit /b
)

