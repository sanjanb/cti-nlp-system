# CTI-NLP Backend Overview

This document provides an overview of the backend system powering the CTI-NLP application, including the architecture, route design, models, and processing flow.

---

## Backend Structure

```

backend/
├── app.py                   # Flask app entry point
├── threat\_ner.py            # Named Entity Recognition using transformers
├── classifier.py            # Threat type classification
├── severity\_predictor.py    # Severity level prediction

```

---

## Tech Stack

| Component    | Description                                |
| ------------ | ------------------------------------------ |
| Flask        | Lightweight web server (REST API)          |
| Flask-CORS   | Enables cross-origin requests for frontend |
| Transformers | Pretrained NER model via HuggingFace       |
| Scikit-learn | Classifier and severity models             |
| Joblib       | Model serialization and loading            |

---

## API Endpoints

### `GET /`

Health check endpoint.

```json
"CTI-NLP backend running."
```

---

### `GET /dashboard`

Serves the frontend HTML dashboard (`index.html`) from:

```html
dashboard/templates/index.html
```

---

### `POST /analyze`

Main endpoint to analyze a given cyber threat report.

#### Input (JSON)

```json
{
  "text": "Emotet is targeting Microsoft users with phishing campaigns..."
}
```

#### 🔹 Output (JSON)

```json
{
  "original_text": "...",
  "entities": [
    { "word": "Emotet", "entity_group": "ORG" },
    { "word": "Microsoft", "entity_group": "ORG" }
  ],
  "threat_type": "Phishing",
  "severity": "High"
}
```

---

## Model Components

### 1. `extract_threat_entities(text)`

- Uses: `dslim/bert-base-NER`
- Purpose: Extract named entities (ORG, LOC, MALWARE, etc.)
- Tool: Hugging Face `pipeline("ner")`

---

### 2. `classify_threat(text)`

- Model: `LogisticRegression`
- Input: TF-IDF features of cleaned text
- Output: Threat category (e.g., Phishing, Malware, Ransomware)
- Artifacts:

  - `models/threat_classifier.pkl`
  - `models/tfidf_vectorizer.pkl`

---

### 3. `predict_severity(text)`

- Model: `RandomForestClassifier`
- Input: TF-IDF vector of threat description
- Output: Risk level (Low, Medium, High)
- Artifacts:

  - `models/severity_model.pkl`
  - `models/tfidf_vectorizer_severity.pkl`

---

## Development Tips

- Always run from the project root:

  ```bash
  set PYTHONPATH=.
  python backend/app.py
  ```

- If models are retrained, don't forget to overwrite:

  - `models/*.pkl`
  - Update any preprocessing changes in `scripts/` accordingly

---

## Related Files

- `scripts/train_threat_classifier.py`
- `scripts/train_severity_model.py`
- `requirements.txt`

---

## Maintainers

- Sanjan Acharya & Team
- 2025 Major Project @ ATME AI & ML Dept.
