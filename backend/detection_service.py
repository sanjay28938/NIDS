import pandas as pd
from pathlib import Path
import joblib
import time
from datetime import datetime
import random

# =====================================
# Project Root Path (AUTO DETECT)
# =====================================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

# =====================================
# Load trained components
# =====================================
print("🚀 Loading AI models...")

model = joblib.load(MODEL_DIR / "ids_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
encoders = joblib.load(MODEL_DIR / "encoders.pkl")

print("✅ Models loaded successfully!")

# =====================================
# Load dataset (Streaming Simulation)
# =====================================
data_path = DATA_DIR / "UNSW_NB15_testing-set.csv"

print("📂 Loading dataset...")

data = pd.read_csv(data_path)

# Drop unnecessary columns
data = data.drop(columns=['id', 'attack_cat'], errors='ignore')

# Separate features
X = data.drop(columns=['label'], errors='ignore')

# =====================================
# Encode categorical features
# =====================================
print("⚙ Encoding categorical features...")

for col, le in encoders.items():
    if col in X.columns:
        X[col] = X[col].astype(str).map(
            lambda x: le.transform([x])[0] if x in le.classes_ else -1
        )

# =====================================
# Match training feature order
# =====================================
X = X[scaler.feature_names_in_]

# =====================================
# Scale features
# =====================================
X_scaled = scaler.transform(X)

print("✅ Dataset ready for streaming!")

# =====================================
# Attack Types (Simulation)
# =====================================
attack_types = [
    "DoS Attack",
    "Probe Attack",
    "R2L Attack",
    "U2R Attack"
]

# =====================================
# Real-Time Detection Simulation
# =====================================
print("\n🔴 Real-Time Intrusion Detection Started...\n")

log_file_path = LOG_DIR / "alerts.log"

with open(log_file_path, "a") as log_file:

    for i in range(len(X_scaled)):

        sample = X_scaled[i].reshape(1, -1)

        prediction = model.predict(sample)[0]

        # =====================================
        # Demo attack simulation (for dashboard)
        # =====================================
        if i % 5 == 0:
            prediction = 1

        prob = model.predict_proba(sample)[0][1]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # =====================================
        # Determine severity level
        # =====================================
        if prob > 0.9:
            severity = "CRITICAL"
        elif prob > 0.7:
            severity = "HIGH"
        elif prob > 0.5:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # =====================================
        # Attack detected
        # =====================================
        if prediction == 1:

            attack_type = random.choice(attack_types)

            message = f"🚨 [{timestamp}] {attack_type} | {severity} | Prob={prob:.2f}"

            print(message)

            log_file.write(
                f"{timestamp} | ATTACK | {attack_type} | {severity} | Prob={prob:.2f}\n"
            )

        # =====================================
        # Normal traffic
        # =====================================
        else:

            message = f"✅ [{timestamp}] Normal Traffic | Prob={prob:.2f}"

            print(message)

            log_file.write(
                f"{timestamp} | NORMAL | NONE | LOW | Prob={prob:.2f}\n"
            )

        # Simulate real-time traffic
        time.sleep(1)

print("\n🛑 Monitoring stopped.")