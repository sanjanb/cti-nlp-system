# Dataset types used in the project

| Dataset Type                       | Purpose                                      | Example / Source                             |
| ---------------------------------- | -------------------------------------------- | -------------------------------------------- |
| Cybersecurity NER Dataset          | Train NER for CVEs, malware, IP, actors      | CyNER / APTNER / MALOnt                      |
| Labeled Threat Text Classification | Train classifier by threat type              | Kaggle NLP-based security datasets           |
| Malicious URL Dataset              | URL-based phishing/malware detection         | Kaggle Malicious URLs dataset                |
| Expert-Annotated CTI Dataset       | Ground-truth IoCs and classifications        | PEASEC / msexchange-server CTI dataset       |
| Synthetic Behavioral Logs          | Feed anomaly detection for severity modeling | Generated synthetic data (no public corpora) |

---

## Dataset Summary and Uses

### 1. `Cybersecurity_Dataset.csv`

| **Contains**               | ✅ Yes / No |
| -------------------------- | ----------- |
| Cleaned Threat Description | ✅ Yes      |
| Threat Category / Type     | ✅ Yes      |
| Severity Score / Level     | ✅ Yes      |
| Named Entities             | ✅ Yes      |
| Suggested Defenses         | ✅ Yes      |

**Use for:**

- **Threat classification** training (`text → category`)
- **Severity prediction** (`text → severity_score`)
- Optional NER verification from `Named Entities (NER)` column

---

### 2. `Cyber-Threat-Intelligence-Custom-Data_new_processed.csv`

| **Contains**            | ✅ Yes / No |
| ----------------------- | ----------- |
| Raw threat reports      | ✅ Yes      |
| Manual annotations      | ✅ Yes      |
| Entity labels/positions | ✅ Yes      |

**Use for:**

- **NER model training** (custom labels like `SOFTWARE`, `malware`, `threat-actor`, `url`, etc.)
- **Contextual relationships & solutions** for future advanced tasks

---

### 3. `cyber-threat-intelligence_all.csv`

| **Contains**       | ✅ Yes / No |
| ------------------ | ----------- |
| Raw reports        | ✅ Yes      |
| Annotated Entities | ✅ Yes      |

**Use for:**

- Combined **NER dataset**
- Use if you want to train on all data at once (then split manually)

Note: We probably don’t need this as we are using the pre-split versions below.

---

### 4. `cyber-threat-intelligence-splited_train.csv`

### 5. `cyber-threat-intelligence-splited_validate.csv`

### 6. `cyber-threat-intelligence-splited_test.csv`

| **Contains**    | ✅ Yes / No                  |
| --------------- | ---------------------------- |
| Raw threat text | ✅ Yes                       |
| Entity labels   | ✅ Yes (partial in test/val) |

**Use for:**

- **NER model training & evaluation**
- Use these directly with HuggingFace/Spacy NER trainers

---

## Recommendations per Task

| **Task**              | **Recommended Dataset(s)**                 |
| --------------------- | ------------------------------------------ |
| Threat Classification | `Cybersecurity_Dataset.csv`                |
| Severity Prediction   | `Cybersecurity_Dataset.csv`                |
| NER Training          | `Custom_Processed.csv` + `splited_*.csv`   |
| NER Evaluation        | `splited_validate.csv`, `splited_test.csv` |

---
