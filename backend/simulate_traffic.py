import time
import random
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "alerts.log"

attacks = [
    "DoS attack detected",
    "Port scan detected",
    "Brute force login attempt",
    "SQL Injection detected"
]

while True:

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    traffic_type = random.choice(["ATTACK", "Normal"])

    if traffic_type == "ATTACK":
        message = random.choice(attacks)
        log = f"{time_now} | ATTACK | {message}\n"
    else:
        log = f"{time_now} | Normal traffic\n"

    with open(LOG_FILE, "a") as f:
        f.write(log)

    print(log)

    time.sleep(3)