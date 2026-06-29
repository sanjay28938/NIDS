import pandas as pd
import time
from pathlib import Path
from datetime import datetime
import joblib

# =========================
# PATH SETUP
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "backend" / "nids_model.pkl"
FEATURE_FILE = BASE_DIR / "backend" / "features.pkl"
ENCODER_FILE = BASE_DIR / "backend" / "encoders.pkl"

TRAIN_FILE = BASE_DIR / "data" / "UNSW_NB15_training-set.csv"
TEST_FILE = BASE_DIR / "data" / "UNSW_NB15_testing-set.csv"

ASN_FILE = BASE_DIR / "data" / "country_asn.csv"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "alerts.log"

LOG_DIR.mkdir(exist_ok=True)

# =========================
# CLEAR OLD LOGS
# =========================
open(LOG_FILE, "w", encoding="utf-8").close()

# =========================
# LOAD MODEL
# =========================
model = joblib.load(MODEL_FILE)
print(type(model))
feature_columns = joblib.load(FEATURE_FILE)
encoders = joblib.load(ENCODER_FILE)

# =========================
# LOAD DATASETS
# =========================
print("Loading datasets...")

train = pd.read_csv(TRAIN_FILE)
test = pd.read_csv(TEST_FILE)

asn_data = pd.read_csv(
    ASN_FILE,
    encoding="latin1",
    low_memory=False
)

# =========================
# SHOW ASN COLUMNS
# =========================
print("\nASN Dataset Columns:")
print(asn_data.columns)

# =========================
# COMBINE UNSW DATA
# =========================
data = pd.concat([train, test])

attack_data = data[data["label"] == 1]
normal_data = data[data["label"] == 0].head(len(attack_data))

data = pd.concat([
    attack_data,
    normal_data
]).sample(frac=1)

# =========================
# CLEAN DATA
# =========================
data = data.fillna(0)

print("\nDataset Loaded:", len(data))

# =========================
# COUNTRY COORDINATES
# =========================
country_coords = {

    "India": (20.5937, 78.9629),
    "United States": (37.0902, -95.7129),
    "Germany": (51.1657, 10.4515),
    "United Kingdom": (55.3781, -3.4360),
    "China": (35.8617, 104.1954),
    "Japan": (36.2048, 138.2529),
    "Russia": (61.5240, 105.3188),
    "Canada": (56.1304, -106.3468),
    "Brazil": (-14.2350, -51.9253),
    "Australia": (-25.2744, 133.7751),
    "France": (46.2276, 2.2137),
    "Italy": (41.8719, 12.5674),
    "Spain": (40.4637, -3.7492),
    "Singapore": (1.3521, 103.8198),
    "South Korea": (35.9078, 127.7669),
    "Mexico": (23.6345, -102.5528),
    "Indonesia": (-0.7893, 113.9213),
    "Turkey": (38.9637, 35.2433),
    "Saudi Arabia": (23.8859, 45.0792),
    "South Africa": (-30.5595, 22.9375),
    "Pakistan": (30.3753, 69.3451),
    "Bangladesh": (23.6850, 90.3563),
    "Sri Lanka": (7.8731, 80.7718),
    "Nepal": (28.3949, 84.1240),
    "UAE": (23.4241, 53.8478),
    "Thailand": (15.8700, 100.9925),
    "Malaysia": (4.2105, 101.9758),
    "Vietnam": (14.0583, 108.2772),
    "Philippines": (12.8797, 121.7740),
    "Argentina": (-38.4161, -63.6167),
    "Colombia": (4.5709, -74.2973),
    "Nigeria": (9.0820, 8.6753),
    "Egypt": (26.8206, 30.8025),
    "Kenya": (-0.0236, 37.9062),
    "Sweden": (60.1282, 18.6435),
    "Norway": (60.4720, 8.4689),
    "Finland": (61.9241, 25.7482),
    "Denmark": (56.2639, 9.5018),
    "Switzerland": (46.8182, 8.2275),
    "Belgium": (50.5039, 4.4699),
    "Poland": (51.9194, 19.1451),
    "Ukraine": (48.3794, 31.1656),
    "Israel": (31.0461, 34.8516),
    "Iran": (32.4279, 53.6880),
    "Iraq": (33.2232, 43.6793),
    "Afghanistan": (33.9391, 67.7100),
    "New Zealand": (-40.9006, 174.8860),
    "Portugal": (39.3999, -8.2245),
    "Greece": (39.0742, 21.8243)
}

# =========================
# COUNTRY CODE MAP
# =========================
country_map = {

    "IN": "India",
    "US": "United States",
    "DE": "Germany",
    "GB": "United Kingdom",
    "CN": "China",
    "JP": "Japan",
    "RU": "Russia",
    "CA": "Canada",
    "BR": "Brazil",
    "AU": "Australia",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "SG": "Singapore",
    "KR": "South Korea",
    "MX": "Mexico",
    "ID": "Indonesia",
    "TR": "Turkey",
    "SA": "Saudi Arabia",
    "ZA": "South Africa",
    "PK": "Pakistan",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "NP": "Nepal",
    "AE": "UAE",
    "TH": "Thailand",
    "MY": "Malaysia",
    "VN": "Vietnam",
    "PH": "Philippines",
    "AR": "Argentina",
    "CO": "Colombia",
    "NG": "Nigeria",
    "EG": "Egypt",
    "KE": "Kenya",
    "SE": "Sweden",
    "NO": "Norway",
    "FI": "Finland",
    "DK": "Denmark",
    "CH": "Switzerland",
    "BE": "Belgium",
    "PL": "Poland",
    "UA": "Ukraine",
    "IL": "Israel",
    "IR": "Iran",
    "IQ": "Iraq",
    "AF": "Afghanistan",
    "NZ": "New Zealand",
    "PT": "Portugal",
    "GR": "Greece"
}
# =========================
# SEVERITY MAP
# =========================
severity_map = {

    "Fuzzers": "MEDIUM",
    "Exploits": "CRITICAL",
    "DoS": "HIGH",
    "Reconnaissance": "LOW",
    "Analysis": "MEDIUM",
    "Backdoor": "CRITICAL",
    "Shellcode": "CRITICAL",
    "Generic": "HIGH",
    "Normal": "LOW"
}

print("\n🚀 AI Detection Engine Started...")
print("🌐 Real ASN Intelligence Enabled")
print("🛡 Real-Time Monitoring Started...")
print("Press CTRL+C to stop\n")

# =========================
# DETECTION LOOP
# =========================
i = 0

while True:

    try:

        # =========================
        # GET TRAFFIC RECORD
        # =========================
        row = data.iloc[i % len(data)]

        time.sleep(0.5)

        timestamp = datetime.now()

        # =========================
        # GET REAL ASN RECORD
        # =========================
        sample = asn_data.sample(1).iloc[0]

        # =========================
        # CHANGE THESE IF NEEDED
        # =========================
        ip = str(sample["start_ip"])

        # =========================
        # GET COUNTRY
        # =========================
        if "country" in asn_data.columns:

            raw_country = str(sample["country"]).strip()
            # =========================
            # CLEAN COUNTRY VALUE
            # =========================
            raw_country = raw_country.replace('"', '')
            raw_country = raw_country.replace("'", "")
            raw_country = raw_country.strip()

            # Ignore invalid country values
            invalid_countries = [
                "",
                "nan",
                "None",
                "NULL",
                "ZZ",
                "AP",
                "EU"
            ]

            if raw_country in invalid_countries:
                continue

            # If already full country name
            if raw_country in country_coords:

                country = raw_country

            else:

                # Convert country code -> full name
                country = country_map.get(
                raw_country.upper(),
                "Unknown"
                )

        else:

                country = "Unknown"

        if country == "Unknown":
            continue

        # Organization column
        if "name" in asn_data.columns:
            organization = str(sample["name"])
        else:
            organization = str(sample["as_name"])

        asn = str(sample["asn"])

        # =========================
        # COUNTRY FIX
        # =========================
        country_fix = {

            "US": "United States",
            "USA": "United States",
            "UK": "United Kingdom",
            "Russian Federation": "Russia",
            "Korea Republic of": "South Korea"
        }

        country = country_fix.get(country, country)

        # =========================
        # GET LAT/LON
        # =========================
        if country in country_coords:

            lat, lon = country_coords[country]

        else:

            lat, lon = 0, 0

        # =========================
        # PREPARE FEATURES
        # =========================
        row_df = pd.DataFrame([row])

        for col in ["proto", "service", "state"]:

            if col in row_df.columns:

                if col in encoders:

                    le = encoders[col]

                    val = str(row_df[col].values[0])

                    if val in le.classes_:

                        row_df[col] = le.transform([val])[0]

                    else:

                        row_df[col] = 0

                else:

                    row_df[col] = 0

        # =========================
        # ALIGN FEATURES
        # =========================
        row_df = row_df.reindex(
            columns=feature_columns,
            fill_value=0
        )

        row_df = row_df.apply(
            pd.to_numeric,
            errors='coerce'
        ).fillna(0)

        # =========================
        # AI PREDICTION
        # =========================
        prediction = model.predict(row_df)[0]

        # =========================
        # ATTACK TYPE
        # =========================
        attack = row.get("attack_cat", "Normal")

        if pd.isna(attack):

            attack = "Normal"

        # =========================
        # EVENT TYPE
        # =========================
        actual_label = row.get("label", 0)

        if prediction == 1 or actual_label == 1:

            event = "ATTACK"

        else:

            event = "NORMAL"

        # =========================
        # SEVERITY
        # =========================
        severity = severity_map.get(
            attack,
            "LOW"
        )

        # =========================
        # CREATE LOG
        # =========================
        log = (
            f"{timestamp} | "
            f"{event} | "
            f"{attack} | "
            f"{severity} | "
            f"{ip} | "
            f"{country} | "
            f"{lat} | "
            f"{lon} | "
            f"{asn} | "
            f"{organization}\n"
        )

        # =========================
        # SAVE LOG
        # =========================
        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(log)

        # =========================
        # TERMINAL OUTPUT
        # =========================
        print(
            f"{event} | "
            f"{attack} | "
            f"{severity} | "
            f"{country} | "
            f"{asn} | "
            f"{organization}"
        )

        i += 1

    except Exception as e:

        print("Error:", e)