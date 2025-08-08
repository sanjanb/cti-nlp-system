# CTI-NLP Training Scripts Overview

This document describes the utility scripts responsible for data preprocessing, model training, and saving outputs for the CTI-NLP backend.

---

## Folder: `scripts/`

```

scripts/
├── train\_threat\_classifier.py     # Train threat category classification model
├── train\_severity\_model.py        # Train risk/severity level prediction model

```

---

## `train_threat_classifier.py`

### 🔧 Function:

- Trains a classifier to predict threat type (e.g., Phishing, Malware)
- Uses TF-IDF vectorization + Logistic Regression (or customizable model)

### Input:

- File: `Cyber-Threat-Intelligence-Custom-Data_new_processed.csv`
- Required Columns:
  - `Cleaned Threat Description`
  - `Threat Category`

### Process:

1. Clean & validate dataset
2. Split into training and test sets
3. TF-IDF vectorization
4. Train logistic regression classifier
5. Save model and vectorizer to `models/`

### Output:

- `models/threat_classifier.pkl`
- `models/tfidf_vectorizer.pkl`

---

## `train_severity_model.py`

### Function:

- Predicts the severity level of threats based on description
- Uses TF-IDF + Random Forest Classifier (or alternative)

### Input:

- File: `Cyber-Threat-Intelligence-Custom-Data_new_processed.csv`
- Required Columns:
  - `Cleaned Threat Description`
  - `Severity Score` or `Risk Level Prediction`

### Process:

1. Clean & validate dataset
2. Encode severity labels
3. TF-IDF vectorization
4. Train random forest classifier
5. Save model and vectorizer

### Output:

- `models/severity_model.pkl`
- `models/severity_vectorizer.pkl`

---

## Notes

- Run these scripts **from the root**:

```bash
python scripts/train_threat_classifier.py
python scripts/train_severity_model.py
```

- Make sure your dataset files are inside `/data`
- All output models are saved inside `/models`

---

## Tips

- Always inspect `df.columns` and `df.head()` before training
- Modify scripts to change model architecture, hyperparameters, or data source
- Add logs or `argparse` if multiple datasets or configs are needed

---

## Maintainers

- Sanjan Acharya & Team
- 2025 Major Project @ ATME AI & ML Dept.
