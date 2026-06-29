import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# Load dataset
train = pd.read_csv("data/UNSW_NB15_training-set.csv")
test = pd.read_csv("data/UNSW_NB15_testing-set.csv")

# Drop ID
train.drop(columns=['label'], inplace=True)
test.drop(columns=['label'], inplace=True)

# Encode categorical columns
encoders = {}
categorical_cols = ['proto', 'service', 'state']

for col in categorical_cols:
    le = LabelEncoder()
    combined = pd.concat([train[col], test[col]], axis=0)
    le.fit(combined)
    train[col] = le.transform(train[col])
    test[col] = le.transform(test[col])
    encoders[col] = le


# Remove any remaining object (string) columns
train = train.select_dtypes(exclude=['object'])
test = test.select_dtypes(exclude=['object'])

# Split features & labels
X_train = train.drop('label', axis=1)
y_train = train['attack_cat']
X_test = test.drop('label', axis=1)
y_test = test['attack_cat']

# Check non-numeric columns
print(X_train.select_dtypes(include='object').columns)
print(X_train[X_train.select_dtypes(include='object').columns].head())

# Scale data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model & scaler
os.makedirs("saved_models", exist_ok=True)
joblib.dump(model, "saved_models/ids_model.pkl")
joblib.dump(scaler, "saved_models/scaler.pkl")
joblib.dump(encoders, "saved_models/encoders.pkl")


print("Model and scaler saved successfully")
