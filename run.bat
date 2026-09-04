@echo off
echo ========================================================
echo   Starting Breast Cancer Detection Web Application
echo ========================================================
if exist "C:\Users\ravir\anaconda3\python.exe" (
    echo Using Anaconda Python environment...
    "C:\Users\ravir\anaconda3\python.exe" app.py
) else (
    echo Using system Python...
    python app.py
)
pause
