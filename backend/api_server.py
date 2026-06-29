from fastapi import FastAPI
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "alerts.log"

@app.get("/")
def home():
    return {"message": "AI NIDS API Running"}

@app.get("/alerts")
def get_alerts():

    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            lines = f.readlines()
    else:
        lines = []

    alerts = []

    for line in lines[-20:]:
        alerts.append(line.strip())

    return {"alerts": alerts}