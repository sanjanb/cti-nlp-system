## STEPS

- NER (Named Entity Recognition)
- Threat Classification
- Severity Prediction
- Model Training & Validation

## PHASE 1: Repository Setup

### 🔹 1.1 Create Folder Structure in the Repo

```bash
cti-nlp-system/
├── backend/             # Flask backend + ML/NLP pipeline
├── dashboard/           # Flask frontend templates
├── data/                # Raw and processed datasets
├── models/              # Saved models or checkpoints
├── scripts/             # Data collection, preprocessing, training scripts
├── utils/               # Helper functions and modules
├── Dockerfile           # Docker image setup
├── docker-compose.yml   # (optional) Multi-service deployment
└── README.md
```

> Push this structure to GitHub now to keep things organized. Start committing from the beginning.

---

## PHASE 2: Dataset Collection & Preprocessing

### 🔹 2.1 Search for Cybersecurity Datasets

Sources:

- [Kaggle: Cybersecurity Threat Intelligence](https://www.kaggle.com/datasets)
- [AlienVault threat reports](https://otx.alienvault.com/)
- [GitHub IOC repositories](https://github.com/search?q=threat+intel+feeds)
- Public Twitter + Reddit feeds (for scraping later)

⏳ **Your action**: Choose one, download it into the `data/` folder, and commit.

---

### 🔹 2.2 Create Preprocessing Script

**File**: `scripts/preprocess.py`

Responsibilities:

- Read `.txt` / `.json` data
- Tokenize, clean text
- Lemmatize
- Store as processed `.csv` or `.json`

> I'll generate this file for you once dataset is added.

---

## PHASE 3: NLP + ML Pipeline

### 🔹 3.1 Named Entity Recognition (NER)

**File**: `backend/threat_ner.py`

- Use `spaCy` + `transformers` to extract IOCs
- Entities: CVEs, IPs, URLs, malware names

```python
from transformers import pipeline
ner = pipeline("ner", model="dslim/bert-base-NER")
```

---

### 🔹 3.2 Classification + Severity Prediction

**File**: `backend/classifier.py`

- Classify threat type: Phishing, Malware, etc.
- Predict severity using:

  - NLP: keyword severity markers
  - AIS-style anomaly detector (simulate logs)

Use `scikit-learn`, `transformers`, or `PyTorch`.

---

## PHASE 4: Backend (API)

### 🔹 4.1 Flask API Setup

**File**: `backend/app.py`

```python
@app.route('/analyze', methods=['POST'])
def analyze_threat():
    # Accept text input
    # Run NER, classification, severity prediction
    # Return results in JSON
```

---

## PHASE 5: Frontend Dashboard

### 🔹 5.1 Flask + HTML Setup

**Files**:

- `dashboard/templates/index.html`
- `dashboard/static/` (for CSS)

Features:

- Input box (for new threat text)
- Results section (entities, classification, severity)
- Table or card UI to show history

> You don’t need React here. Just HTML+Jinja for simplicity.

---

## PHASE 6: Dockerize Everything

### 🔹 6.1 Docker Setup

**File**: `Dockerfile`

```dockerfile
FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "backend/app.py"]
```

**Optional**: `docker-compose.yml` to run both frontend and backend (if split)

---

## PHASE 7: Testing & Deployment

### 🔹 7.1 Test Locally

```bash
python backend/app.py
# OR
flask run
```

### 🔹 7.2 Test Docker

```bash
docker build -t cti-nlp .
docker run -p 5000:5000 cti-nlp
```

---

## 🔁 Weekly Checklist

| Task                       | Status |
| -------------------------- | ------ |
| Create folder structure    | ✅     |
| Find/download dataset      | ⏳     |
| Preprocessing script       | ⏳     |
| NER + classifier code      | ⏳     |
| Flask API setup            | ⏳     |
| Basic frontend UI          | ⏳     |
| Docker container setup     | ⏳     |
| Test + document everything | ⏳     |

---

## 📦 Suggested Initial Commits

```bash
git add .
git commit -m "Initial project structure and docs"
git push origin main
```

---

Would you like me to:

- 📁 Create the starter files for `preprocess.py`, `app.py`, and `index.html` now?
- 📦 Build the full Dockerfile with `requirements.txt`?

Just say “start with code” and I’ll begin building those now ✅
