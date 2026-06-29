from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def home():
    return {"message": "NIDS AI Backend Running"}

@app.get("/start-detection")
def start_detection():
    subprocess.Popen(["python", "backend/detection_service.py"])
    return {"status": "Detection Started"}

@app.get("/alerts")
def get_alerts():
    with open("logs/alerts.log", "r") as f:
        data = f.readlines()
    return {"alerts": data[-20:]}
