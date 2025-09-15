# Project Review 1: Model Selection & Metrics (PPT Script)

---

## Slide 0: Foundational Concepts

- **Supervised Learning:**
  - We use labeled data to train models to predict threat categories, severity, and named entities.
- **Classification Metrics:**
  - Accuracy, Precision, Recall, F1-score: These help us judge how well our models distinguish between threat types and severities.
- **NLP Pipeline:**
  - Data cleaning → Tokenization → Feature extraction (TF-IDF, embeddings) → Model training → Evaluation
- **Why These Matter for CTI:**
  - Cybersecurity text is noisy and imbalanced; robust metrics and preprocessing are essential for reliable automation.

---

---

## Slide 1: Title

- **Project:** Cyber Threat Intelligence NLP System
- **Focus:** Model Selection, Metrics, and Evaluation

---

## Slide 2: Model Selection Approach

- Compared multiple models: Logistic Regression, SVM, Random Forest, XGBoost, LSTM, BERT, DistilBERT
- Used classical ML and deep learning for both classification and NER
- Ensemble methods for best performance

---

## Slide 3: Metrics for Model Selection

- **Classification:** Accuracy, Precision, Recall, F1-score
- **NER:** Entity-level F1-score
- **Validation:** 5-fold cross-validation, holdout test set
- **Visualization:** F1-score bar plots, confusion matrices

---

## Slide 4: Threat Classifier Results

- **Best Model:** Ensemble (Logistic Regression + XGBoost)
- **Why:** Best F1-score, robust to class imbalance, interpretable
- **Visualizations:**
  - ![F1-score by class](../../assets/review1/threat_classifier_f1.png)
  - ![Confusion Matrix](../../assets/review1/threat_classifier_cm.png)

---

## Slide 5: Severity Prediction Results

- **Best Model:** XGBoost with custom features
- **Why:** Highest F1, handled imbalance
- (Add similar F1/confusion matrix plots if available)

---

## Slide 6: NER Results

- **Best Model:** Fine-tuned DistilBERT
- **Why:** Highest entity-level F1, robust to noisy text
- (Add entity-level F1-score plot if available)

---

## Slide 7: What to Tell the Guide

- We systematically compared models using robust metrics and visualizations
- Chose models that balance accuracy, speed, and interpretability
- Visualizations (F1, confusion matrix) show strengths and weaknesses
- Our approach is reproducible and data-driven

---

## Slide 8: Q&A

- Ready to discuss model choices, metrics, and next steps

---

_Prepared for Project Review 1: Model Selection and Evaluation_
