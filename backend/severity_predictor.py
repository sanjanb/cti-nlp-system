def predict_severity(text):
    # MOCK function - replace later with ML model
    if "critical" in text.lower() or "breach" in text.lower():
        return "High"
    elif "suspicious" in text.lower():
        return "Medium"
    else:
        return "Low"
