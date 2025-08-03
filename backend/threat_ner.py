def extract_threat_entities(text):
    # MOCK function - simulate NER output
    entities = []
    words = text.split()
    for word in words:
        if "http" in word:
            entities.append({"type": "URL", "value": word})
        elif "Microsoft" in word or "Linux" in word:
            entities.append({"type": "OS", "value": word})
        elif "Qbot" in word or "Emotet" in word:
            entities.append({"type": "Malware", "value": word})
    return entities
