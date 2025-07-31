from transformers import pipeline

# Load NER pipeline once
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def extract_threat_entities(text):
    results = ner_pipeline(text)
    extracted = []

    for entity in results:
        extracted.append({
            "type": entity['entity_group'],
            "value": entity['word']
        })

    return extracted
