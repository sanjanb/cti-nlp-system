# Project Review 1: Model Selection and Evaluation

## 1. Introduction

This presentation focuses on the core machine learning and NLP modeling work for our Cyber Threat Intelligence NLP System. We will cover the process of dataset selection, preprocessing, feature engineering, model experimentation, and the rationale behind our final model choices.

## 2. Dataset Selection

- **Source Variety:** We curated datasets from multiple sources relevant to cyber threat intelligence, including Twitter, dark web forums, and the MITRE ATT&CK framework.
- **Relevance:** Datasets were chosen to cover a wide range of threat types, severity levels, and real-world language used in cybersecurity incidents.
- **Final Datasets:**
  - `cyber-threat-intelligence_all.csv` (comprehensive CTI dataset)
  - `Cybersecurity_Dataset.csv` (general cybersecurity incidents)
  - Custom NER-prepared datasets for entity recognition tasks

## 3. Data Preprocessing

- **Cleaning:**
  - Removed duplicates, nulls, and irrelevant records
  - Standardized text (lowercasing, punctuation removal, URL/user mention stripping)
- **Tokenization:**
  - Used spaCy and NLTK for robust tokenization
- **Label Encoding:**
  - Encoded categorical labels for classification and NER tasks
- **NER Preparation:**
  - Converted annotated data to spaCy-compatible JSONL format for training

## 4. Feature Engineering

- **Text Vectorization:**
  - TF-IDF vectorization for classical ML models
  - Word embeddings (spaCy, transformers) for deep learning models
- **Custom Features:**
  - Extracted threat-specific keywords, n-grams, and context windows
  - Severity heuristics (e.g., presence of CVE, malware names)
- **Dimensionality Reduction:**
  - Used feature selection and PCA for optimal model input

## 5. Model Experimentation

- **Classical ML Models:**
  - Logistic Regression, SVM, Random Forest, XGBoost
  - Baseline for threat classification and severity prediction
- **Deep Learning Models:**
  - LSTM, BiLSTM, and transformer-based models (BERT, DistilBERT)
  - Used for both classification and NER
- **Ensemble Approaches:**
  - Combined predictions from multiple models for improved robustness

## 6. Model Selection Process

- **Evaluation Metrics:**
  - Accuracy, Precision, Recall, F1-score for classification
  - Entity-level F1 for NER
- **Cross-Validation:**
  - 5-fold cross-validation to ensure generalizability
- **Hyperparameter Tuning:**
  - Grid search and random search for optimal parameters
- **Ablation Studies:**
  - Tested impact of different features and model architectures

## 7. Final Model Choice & Rationale

- **Threat Classification:**
  - **Best Model:** Ensemble of Logistic Regression and XGBoost with TF-IDF features
  - **Why:** Outperformed deep models on limited data, faster inference, interpretable
  - **Why Not Others:** Transformers required more data and compute, marginal gains
- **Severity Prediction:**
  - **Best Model:** XGBoost with custom severity features
  - **Why:** Best F1-score, handled class imbalance well
  - **Why Not Others:** Simpler models underfit, deep models overfit
- **NER (Entity Recognition):**
  - **Best Model:** Fine-tuned DistilBERT
  - **Why:** Achieved highest entity-level F1, robust to noisy text
  - **Why Not Others:** spaCy and LSTM models had lower recall on rare entities

## 8. Testing & Validation

- **Holdout Test Set:**
  - Evaluated all final models on unseen data
- **Results:**
  - Consistent performance with cross-validation
  - Error analysis guided further improvements

## 9. Conclusion

Our systematic approach—combining classical ML, deep learning, and ensemble methods—enabled us to select the most effective models for each CTI-NLP task. The chosen models balance accuracy, speed, and interpretability, making them suitable for real-world deployment.

---

_Prepared for Project Review 1: Model Selection and Evaluation_
