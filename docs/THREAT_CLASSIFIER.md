> _This file documents the development of the **Threat Classification** component in the CTI-NLP System._

---

# Threat Type Classification Module

The **Threat Classifier** predicts the type of cyber threat (e.g., Phishing, Malware, Ransomware) from unstructured threat descriptions. This classification helps analysts understand the nature of threats quickly and aids in automated threat triage.

---

## Objective

To classify cybersecurity threat descriptions into pre-defined **threat categories**, such as:

- Phishing
- Malware
- Botnet
- DDoS
- Spyware
- Ransomware
  _(exact categories depend on training data)_

---

## Dataset Used

- **File:** `Cybersecurity_Dataset.csv`
- **Source:** Provided structured dataset.
- **Key Columns:**

  - `Cleaned Threat Description` → Input feature
  - `Threat Category` → Target variable (multi-class label)

---

## Preprocessing

- Standardized column names by removing leading/trailing spaces.
- Dropped rows with missing values in text or category columns.
- Converted all text data to lowercase during vectorization.

---

## Model Pipeline

| Step               | Technique                               |
| ------------------ | --------------------------------------- |
| Text Preprocessing | `TfidfVectorizer` (max 5000 features)   |
| Model              | `LogisticRegression` (max_iter=1000)    |
| Train/Test Split   | 80% train, 20% test (random_state=42)   |
| Evaluation         | `sklearn.metrics.classification_report` |

---

## Files Created

- `models/tfidf_vectorizer.pkl` → TF-IDF vectorizer
- `models/threat_classifier.pkl` → Trained Logistic Regression model

---

## Example Prediction Flow

1. Text is received from the frontend or API.
2. Preprocessed using the saved TF-IDF vectorizer.
3. The logistic regression model predicts the threat category.
4. Category is returned to the frontend along with severity and entities.

---

## Sample Output

```json
{
  "original_text": "A phishing email spoofing Microsoft login to collect credentials.",
  "entities": [...],
  "threat_type": "Phishing",
  "severity": "Medium"
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

- Training script: `scripts/train_threat_classifier.py`
- Inference logic: `backend/classifier.py`
