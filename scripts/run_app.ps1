# Run from the project root.

Write-Host "Starting Insurance AI Copilot..."

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload"
)

Start-Sleep -Seconds 3

streamlit run dashboard/streamlit_app.py
