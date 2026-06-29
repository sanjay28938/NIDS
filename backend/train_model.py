import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_FILE = BASE_DIR / "data" / "UNSW_NB15_training-set.csv"

MODEL_FILE = BASE_DIR / "backend" / "nids_model.pkl"
FEATURE_FILE = BASE_DIR / "backend" / "features.pkl"
ENCODER_FILE = BASE_DIR / "backend" / "encoders.pkl"

# =========================
# LOAD DATA
# =========================
data = pd.read_csv(TRAIN_FILE)
data = data.fillna(0)

# =========================
# ENCODE CATEGORICAL
# =========================
categorical_cols = ["proto", "service", "state"]

encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))
    encoders[col] = le

# =========================
# FEATURES + LABEL
# =========================
X = data.drop(["attack_cat", "label"], axis=1)
y = data["label"]

# =========================
# TRAIN MODEL
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# =========================
# EVALUATE
# =========================
pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)

print("Model Accuracy:", accuracy)

# =========================
# SAVE EVERYTHING
# =========================
joblib.dump(model, MODEL_FILE)
joblib.dump(X.columns.tolist(), FEATURE_FILE)
joblib.dump(encoders, ENCODER_FILE)

print("✅ Model + Features + Encoders saved")