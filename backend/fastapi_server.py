from fastapi import FastAPI
import pandas as pd
from pathlib import Path

app = FastAPI()

LOG_FILE = Path("../logs/alerts.log")

@app.get("/alerts")
def get_alerts():

    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            lines = f.readlines()

        return {"alerts": lines[-20:]}

    return {"alerts": []}