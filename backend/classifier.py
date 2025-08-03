def classify_threat(text):
    # MOCK function - replace later with real model
    keywords = {
        "phishing": "Phishing",
        "malware": "Malware",
        "ransomware": "Ransomware",
        "ddos": "DDoS"
    }
    for keyword, label in keywords.items():
        if keyword in text.lower():
            return label
    return "General Threat"
