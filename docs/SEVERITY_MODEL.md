> _This file documents the development of the **Severity Prediction** component in the CTI-NLP System._

---

# Severity Prediction Module

The **Severity Prediction Model** is responsible for automatically estimating the risk level (Low, Medium, High) of a cybersecurity threat based on its textual description. This prediction plays a key role in prioritizing responses in cybersecurity operations.

---

## Objective

To classify textual threat descriptions into **three severity levels**:

- `Low`
- `Medium`
- `High`

---

## Dataset Used

- **File:** `Cybersecurity_Dataset.csv`
- **Source:** Provided dataset containing threat intelligence metadata.
- **Key Columns:**

  - `Cleaned Threat Description` → Input feature
  - `Severity Score` (range: 1 to 5) → Raw target

---

## Preprocessing

- Renamed columns and removed extra whitespaces.
- Removed rows with missing values in required fields.
- Mapped `Severity Score` (1–5) into discrete classes:

  | Original Score | Mapped Class |
  | -------------- | ------------ |
  | 1–2            | Low          |
  | 3              | Medium       |
  | 4–5            | High         |

---

## Model Pipeline

| Step               | Technique                               |
| ------------------ | --------------------------------------- |
| Text Preprocessing | `TfidfVectorizer` (max 5000 features)   |
| Model              | `RandomForestClassifier`                |
| Train/Test Split   | 80% train, 20% test (random_state=42)   |
| Evaluation         | `sklearn.metrics.classification_report` |

---

## Files Created

- `models/severity_vectorizer.pkl` → TF-IDF vectorizer
- `models/severity_model.pkl` → Trained Random Forest model

---

## Example Prediction Flow

1. User submits threat description via frontend.
2. Text is vectorized using TF-IDF.
3. Random Forest model predicts the severity label.
4. Result is returned as part of the backend `/analyze` response.

---

## Sample Output

```json
{
  "original_text": "Emotet botnet spreading via phishing emails and malicious attachments.",
  "entities": [...],
  "threat_type": "Phishing",
  "severity": "High"
}
```

---

## Technologies Used

- Python
- Scikit-learn
- Pandas
- Joblib

---

## Script Location

- Training script: `scripts/train_severity_model.py`
- Inference code: `backend/severity_predictor.py`
