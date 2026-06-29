import pandas as pd
import joblib

# Load artifacts
model = joblib.load("saved_models/ids_model.pkl")
scaler = joblib.load("saved_models/scaler.pkl")
encoders = joblib.load("saved_models/encoders.pkl")

# Load data
data = pd.read_csv("data/UNSW_NB15_testing-set.csv")

# Drop non-feature columns
for col in ['id', 'label', 'attack_cat']:
    if col in data.columns:
        data.drop(columns=[col], inplace=True)

# Encode categorical columns using TRAINED encoders
categorical_cols = ['proto', 'service', 'state']
for col in categorical_cols:
    if col in data.columns:
        le = encoders[col]
        data[col] = data[col].map(
            lambda x: x if x in le.classes_ else le.classes_[0]
        )
        data[col] = le.transform(data[col])

# Ensure column order matches training
data = data[scaler.feature_names_in_]

# Scale
data_scaled = scaler.transform(data)

# Predict
predictions = model.predict(data_scaled)

probs = model.predict_proba(data_scaled)

for i in range(10):
    attack_prob = probs[i][1]
    print(
        f"Packet {i+1}: "
        f"{'🚨 ATTACK' if attack_prob > 0.5 else '✅ NORMAL'} "
        f"(Attack probability = {attack_prob:.2f})"
    )


