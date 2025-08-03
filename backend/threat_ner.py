from transformers import pipeline

# Load the HuggingFace pretrained NER pipeline
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def extract_threat_entities(text):
    try:
        entities = ner_pipeline(text)
        return entities
    except Exception as e:
        return [{"error": str(e)}]
