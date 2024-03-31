@echo off
REM Check if the venv directory exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.

    REM Activate the virtual environment
    CALL venv\Scripts\activate.bat

    REM Install requirements from requirements.txt
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    echo Dependencies installed.
) ELSE (
    REM Activate the virtual environment
    CALL venv\Scripts\activate.bat
)

REM Start the GUI
streamlit run gui.py


