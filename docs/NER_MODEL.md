# Named Entity Recognition (NER) Module

> This document outlines the Named Entity Recognition component used in the CTI-NLP System.

---

## Objective

The NER module is designed to extract meaningful cybersecurity-related entities from unstructured text. These entities help analysts quickly understand the context and focus of threat reports.

### Types of Entities Extracted:

- Malware or tools (e.g., Emotet, Qakbot)
- Threat actors or organizations (e.g., Lazarus Group, Microsoft)
- Operating systems or platforms (e.g., Windows, Linux)
- Domains, URLs, IP addresses _(if present)_

---

## Model Information

| Parameter        | Value                    |
| ---------------- | ------------------------ |
| **Model Name**   | `dslim/bert-base-NER`    |
| **Framework**    | HuggingFace Transformers |
| **Trained On**   | CoNLL-2003 dataset       |
| **Entity Types** | ORG, LOC, PER, MISC      |
| **Use Case Fit** | General-purpose NER      |
| **Status**       | Production-ready for MVP |

🔗 Model Link: [dslim/bert-base-NER on HuggingFace](https://huggingface.co/dslim/bert-base-NER)

---

## Integration Details

The model is integrated using HuggingFace's `pipeline()` utility, which loads the NER model and tokenizer.

### Inference Code (`backend/threat_ner.py`):

```python
from transformers import pipeline

# Load the pipeline
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)

def extract_threat_entities(text):
    try:
        return ner_pipeline(text)
    except Exception as e:
        return [{"error": str(e)}]
```

---

## Example Output

### Input:

```text
Emotet malware is targeting Microsoft Outlook users across Europe.
```

### Output:

```json
[
  { "entity_group": "MISC", "word": "Emotet", "score": 0.96 },
  { "entity_group": "ORG", "word": "Microsoft", "score": 0.99 },
  { "entity_group": "LOC", "word": "Europe", "score": 0.98 }
]
```

---

## Technologies Used

- Python
- HuggingFace Transformers
- Pretrained BERT model

---

## File Locations

- Inference logic: `backend/threat_ner.py`
- No training script needed (pretrained model)

---

## Future Scope

To improve domain specificity, a fine-tuned NER model trained on cybersecurity corpora (e.g., threat reports, STIX-tagged indicators) can replace the current one.
