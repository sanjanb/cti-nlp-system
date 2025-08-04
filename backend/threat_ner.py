from transformers import pipeline

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def extract_threat_entities(text):
    entities = ner_pipeline(text)
    grouped = {}

    for ent in entities:
        label = ent["entity_group"]
        word = ent["word"]

        if label not in grouped:
            grouped[label] = []
        if word not in grouped[label]:
            grouped[label].append(word)

    return grouped
