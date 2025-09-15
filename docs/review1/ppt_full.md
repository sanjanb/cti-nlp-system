# Project Review 1: End-to-End CTI-NLP System (Comprehensive PPT)

---

## Slide 1: Title & Motivation

_See: [ppt_foundations_expert.md](ppt_foundations_expert.md), [../README.md](../README.md), [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) for foundational concepts, project summary, and motivation._

- **Project:** Cyber Threat Intelligence NLP System
- **Goal:** Automate extraction and classification of cyber threats from unstructured text
- **Motivation:**
  - Real-world attacks are increasing
  - Manual threat analysis is slow and error-prone
  - Our system enables faster, data-driven defense

---

## Slide 2: Problem Statement

_See: [../02-architecture/1. SCRIPTS_OVERVIEW.md](../02-architecture/1. SCRIPTS_OVERVIEW.md), [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for project scope and CTI context._

- Extract actionable threat intelligence from noisy, real-world text (tweets, forums, reports)
- Classify threat type, predict severity, and extract key entities

---

## Slide 3: Data Collection & Sources

_See: [../04-development/DATASET.md](../04-development/DATASET.md), [../01-getting-started/USER_MANUAL.md](../01-getting-started/USER_MANUAL.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for data sources and collection details._

- **Sources:**
  - Twitter (live and historical)
  - MITRE ATT&CK
  - Dark web forums
  - Public cybersecurity datasets
- **Proof:** Example raw data snippet:
  - `"phishing email with malicious link targeting companyX"`

---

## Slide 4: Data Exploration & Insights

_See: [../04-development/DATASET.md](../04-development/DATASET.md), [../03-models/MODEL_ENHANCEMENT_REPORT.md](../03-models/MODEL_ENHANCEMENT_REPORT.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for data analysis and statistics._

- **Threat Category Distribution:**
  - ![Threat Category Distribution](../../assets/review1/threat_category_distribution.png)
- **Severity Score Distribution:**
  - ![Severity Score Distribution](../../assets/review1/severity_score_distribution.png)
- **Text Length Distribution:**
  - ![Text Length Distribution](../../assets/review1/text_length_distribution.png)
- **Stats:** 4 categories, 1100 samples, avg. text length 42.7

---

## Slide 5: Preprocessing Pipeline

_See: [../04-development/DATASET.md](../04-development/DATASET.md), [../02-architecture/1. SCRIPTS_OVERVIEW.md](../02-architecture/1. SCRIPTS_OVERVIEW.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for preprocessing steps and rationale._

- Cleaning: remove noise, standardize text
- Tokenization: spaCy, NLTK
- Label encoding for classification/NER
- NER data: converted to spaCy/transformers format
- **Proof:** Example cleaned text, label mapping table

---

## Slide 6: Feature Engineering

_See: [../04-development/DATASET.md](../04-development/DATASET.md), [../02-architecture/AI-ML-ARCHITECTURE.md](../02-architecture/AI-ML-ARCHITECTURE.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for feature engineering details._

- TF-IDF for classical models
- Word embeddings (spaCy, transformers) for deep models
- Custom features: threat keywords, n-grams, CVE presence
- **Proof:** Feature importance plot (add if available)

---

## Slide 7: Model Selection & Experiments

_See: [../03-models/2. THREAT_CLASSIFIER.md](../03-models/2. THREAT_CLASSIFIER.md), [../03-models/3. SEVERITY_MODEL.md](../03-models/3. SEVERITY_MODEL.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md), [../03-models/7. THREAT_CLASSIFIER_LOGISTIC.md](../03-models/7. THREAT_CLASSIFIER_LOGISTIC.md), [../03-models/6. WHY_ENSEMBLE.md](../03-models/6. WHY_ENSEMBLE.md), [../07-research/ACADEMIC_JUSTIFICATION_REPORT.md](../07-research/ACADEMIC_JUSTIFICATION_REPORT.md), [../07-research/GUIDE_PRESENTATION_SUMMARY.md](../07-research/GUIDE_PRESENTATION_SUMMARY.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for model selection and experiments._

### Models Considered & Selection Rationale

- **Threat Classification:**
  - Tried: Logistic Regression, SVM, Random Forest, XGBoost, LSTM, BERT, DistilBERT
  - **Selected:** Ensemble (Logistic Regression + XGBoost)
  - **Why:** Best F1-score, robust to class imbalance, interpretable, fast for real-time use
- **Severity Prediction:**
  - Tried: Random Forest, XGBoost, SVM, BERT
  - **Selected:** XGBoost with custom features
  - **Why:** Best accuracy and F1, handles non-linear relationships, interpretable feature importances
- **NER:**
  - Tried: spaCy, BERT, DistilBERT, Regex
  - **Selected:** DistilBERT (HuggingFace Transformers)
  - **Why:** Best entity-level F1, strong generalization, easy integration


### Model Selection Process

- All models evaluated using 5-fold cross-validation
- Metrics: Accuracy, F1-score, confusion matrix, training time
- Hyperparameters for each model were optimized using grid search over a predefined parameter space
- Ensemble and hybrid approaches tested for threat classification

### Comparative Results Table (Sample)

| Task                  | Model                  | Accuracy | F1-score | Training Time |
| --------------------- | ---------------------- | -------- | -------- | ------------- |
| Threat Classification | Logistic Regression    | 0.24     | 0.20     | 0.02s         |
| Threat Classification | XGBoost                | 0.25     | 0.21     | 0.10s         |
| Threat Classification | **Ensemble (Final)**   | **0.27** | **0.23** | 0.12s         |
| Severity Prediction   | Random Forest          | 0.36     | 0.28     | 0.05s         |
| Severity Prediction   | **XGBoost (Final)**    | **0.40** | **0.29** | 0.07s         |
| NER                   | spaCy                  | 0.78     | 0.75     | 0.20s         |
| NER                   | **DistilBERT (Final)** | **0.82** | **0.80** | 0.30s         |

### Model Strengths & Limitations

- **Logistic Regression:** Fast, interpretable, but limited for non-linear patterns
- **XGBoost:** High accuracy, handles feature interactions, but slower than linear models
- **DistilBERT:** High F1 for NER, robust, but requires more compute

---

## Slide 7a: Proof of Concept (POC) – Model Output Example

_See: [../03-models/2. THREAT_CLASSIFIER.md](../03-models/2. THREAT_CLASSIFIER.md), [../03-models/3. SEVERITY_MODEL.md](../03-models/3. SEVERITY_MODEL.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md)_

**Input:**

> "Emotet malware is targeting Microsoft Outlook users across Europe."

**Model Outputs:**

- **Threat Type:** Malware
- **Severity:** High
- **Entities:**
  - Emotet (MISC)
  - Microsoft (ORG)
  - Europe (LOC)

**API JSON Output:**

```json
{
  "original_text": "Emotet malware is targeting Microsoft Outlook users across Europe.",
  "entities": [
    { "entity_group": "MISC", "word": "Emotet", "score": 0.96 },
    { "entity_group": "ORG", "word": "Microsoft", "score": 0.99 },
    { "entity_group": "LOC", "word": "Europe", "score": 0.98 }
  ],
  "threat_type": "Malware",
  "severity": "High"
}
```

---

## Slide 8: Metrics & Visualizations

_See: [../03-models/2. THREAT_CLASSIFIER.md](../03-models/2. THREAT_CLASSIFIER.md), [../03-models/3. SEVERITY_MODEL.md](../03-models/3. SEVERITY_MODEL.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md), [../03-models/MODEL_ENHANCEMENT_REPORT.md](../03-models/MODEL_ENHANCEMENT_REPORT.md), [../07-research/ACADEMIC_JUSTIFICATION_REPORT.md](../07-research/ACADEMIC_JUSTIFICATION_REPORT.md), [../07-research/GUIDE_PRESENTATION_SUMMARY.md](../07-research/GUIDE_PRESENTATION_SUMMARY.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for metrics and evaluation._

- **Threat Classifier:**
  - ![F1-score by class](../../assets/review1/threat_classifier_f1.png)
  - ![Confusion Matrix](../../assets/review1/threat_classifier_cm.png)
- **Severity Model:**
  - ![F1-score by severity](../../assets/review1/severity_f1.png)
  - ![Confusion Matrix](../../assets/review1/severity_cm.png)
- **NER:** (Add entity-level F1 plot if available)

---

## Slide 9: Error Analysis & Lessons Learned

_See: [../06-testing/TEST_GUIDE.md](../06-testing/TEST_GUIDE.md), [../06-testing/TESTING.md](../06-testing/TESTING.md), [../03-models/MODEL_ENHANCEMENT_REPORT.md](../03-models/MODEL_ENHANCEMENT_REPORT.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for error analysis and lessons._

- Where do models struggle? (e.g., rare classes, ambiguous text)
- How did we address: class imbalance, noisy data
- **Proof:** Example misclassified samples (add if available)

---

## Slide 10: Final Model Justification

_See: [../03-models/2. THREAT_CLASSIFIER.md](../03-models/2. THREAT_CLASSIFIER.md), [../03-models/3. SEVERITY_MODEL.md](../03-models/3. SEVERITY_MODEL.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md), [../03-models/6. WHY_ENSEMBLE.md](../03-models/6. WHY_ENSEMBLE.md), [../07-research/ACADEMIC_JUSTIFICATION_REPORT.md](../07-research/ACADEMIC_JUSTIFICATION_REPORT.md), [../07-research/GUIDE_PRESENTATION_SUMMARY.md](../07-research/GUIDE_PRESENTATION_SUMMARY.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for justification and rationale._

- **Threat Classification:** Ensemble (LogReg + XGBoost)
- **Severity:** XGBoost with custom features
- **NER:** DistilBERT
- **Why:** Best F1, robust, interpretable, fast

---

## Slide 11: Deployment & Real-World Use

_See: [../02-architecture/5. BACKEND_OVERVIEW.md](../02-architecture/5. BACKEND_OVERVIEW.md), [../05-deployment/DEPLOYMENT.md](../05-deployment/DEPLOYMENT.md), [../01-getting-started/USER_MANUAL.md](../01-getting-started/USER_MANUAL.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for deployment and API details._

- REST API (FastAPI backend)
- Dockerized for easy deployment
- **Proof:**
  - [API code link](../../backend/main.py)
  - [Dockerfile link](../../Dockerfile)
  - Screenshot of running API (add if available)

---

## Slide 12: Challenges & Future Work

_See: [../08-planning/96. PLAN-2.md](../08-planning/96. PLAN-2.md), [../08-planning/97. PLAN-MVP.md](../08-planning/97. PLAN-MVP.md), [../03-models/MODEL_ENHANCEMENT_REPORT.md](../03-models/MODEL_ENHANCEMENT_REPORT.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for challenges and roadmap._

- Data quality, class imbalance, real-time ingestion
- Next: more data, advanced models, dashboard, integration

---

## Slide 13: References & Acknowledgements

_See: [../README.md](../README.md), [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md), [../01-getting-started/USER_MANUAL.md](../01-getting-started/USER_MANUAL.md), [../05-deployment/DEPLOYMENT.md](../05-deployment/DEPLOYMENT.md), [../03-models/2. THREAT_CLASSIFIER.md](../03-models/2. THREAT_CLASSIFIER.md), [../03-models/3. SEVERITY_MODEL.md](../03-models/3. SEVERITY_MODEL.md), [../03-models/4. NER_MODEL.md](../03-models/4. NER_MODEL.md), [../03-models/6. WHY_ENSEMBLE.md](../03-models/6. WHY_ENSEMBLE.md), [../03-models/7. THREAT_CLASSIFIER_LOGISTIC.md](../03-models/7. THREAT_CLASSIFIER_LOGISTIC.md), [../03-models/MODEL_ENHANCEMENT_REPORT.md](../03-models/MODEL_ENHANCEMENT_REPORT.md), [../04-development/DATASET.md](../04-development/DATASET.md), [../06-testing/TEST_GUIDE.md](../06-testing/TEST_GUIDE.md), [../06-testing/TESTING.md](../06-testing/TESTING.md), [../07-research/ACADEMIC_JUSTIFICATION_REPORT.md](../07-research/ACADEMIC_JUSTIFICATION_REPORT.md), [../07-research/GUIDE_PRESENTATION_SUMMARY.md](../07-research/GUIDE_PRESENTATION_SUMMARY.md), [../08-planning/96. PLAN-2.md](../08-planning/96. PLAN-2.md), [../08-planning/97. PLAN-MVP.md](../08-planning/97. PLAN-MVP.md), [ppt_foundations_expert.md](ppt_foundations_expert.md) for further reading and resources._

- Datasets: MITRE, Twitter, public CTI
- Libraries: scikit-learn, transformers, spaCy, FastAPI
- [GitHub repo link](https://github.com/sanjanb/cti-nlp-system)

---

## Slide 14: Q&A

- Ready to discuss technical details, results, and next steps

---

_Prepared for Project Review 1: End-to-End CTI-NLP System_
