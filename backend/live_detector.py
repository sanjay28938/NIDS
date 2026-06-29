import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(BASE_DIR / "backend" / "nids_model.pkl")
feature_columns = joblib.load(BASE_DIR / "backend" / "features.pkl")
encoders = joblib.load(BASE_DIR / "backend" / "encoders.pkl")
print("Model Loaded:", model)
print("Features:", len(feature_columns))
print("Encoders:", encoders.keys())

def extract_features(packet):

    # protocol detection
    proto = "other"

    if packet.haslayer("TCP"):
        proto = "tcp"
    elif packet.haslayer("UDP"):
        proto = "udp"

    # packet size
    packet_len = len(packet)

    # source IP
    src_ip = "Unknown"
    if packet.haslayer("IP"):
        src_ip = packet["IP"].src

    return {
        "proto": proto,
        "packet_len": packet_len,
        "src_ip": src_ip
    }

from scapy.all import sniff

def test(packet):
    features = extract_features(packet)
    print(features)

sniff(prn=test, count=5)