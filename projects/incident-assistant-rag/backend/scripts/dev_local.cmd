@echo off
setlocal
set "ROOT=%~dp0.."
cd /d "%ROOT%"
for %%I in ("%~dp0..\..\..\..") do set "REPO_ROOT=%%~fI"
call "%REPO_ROOT%\.venv\Scripts\activate.bat"
pip install -r requirements.txt || exit /b 1
echo Starting API at http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
