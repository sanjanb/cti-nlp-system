![header](assets/header.png)

#  AI-Powered Cyber Threat Intelligence System using NLP & FastAPI

A predictive Cyber Threat Intelligence (CTI) system that leverages **Natural Language Processing (NLP)** and **AI-based classification** to extract meaningful cyber threat indicators from unstructured text, categorize threat types, predict severity levels, and visualize insights through an interactive, modular web interface.



##  Table of Contents

- [ Overview](#overview)
- [ Features](#features)
- [ Project Structure](#project-structure)
- [ Technology Stack](#technology-stack)
- [ Getting Started](#getting-started)
- [ Testing the Application](#testing-the-application)
- [ Documentation](#documentation)
- [ Contributing](#contributing)
- [ License](#license)
- [ Maintainers](#maintainers)



##  Overview

In today’s cyber threat landscape, real-time intelligence is crucial. This platform uses **NLP-based entity recognition**, **machine learning-based threat classification**, and **severity prediction models** to generate actionable insights from threat reports and forum data.

The system is designed for analysts and SOC teams to **triage, investigate, and act** — all within one command-center styled dashboard.



##  Features

-  **Named Entity Recognition (NER)** for extracting IOCs (IP addresses, malware names, CVEs, etc.)
-  **Threat Classification** into categories like Phishing, Malware, APTs, Ransomware
-  **Severity Level Prediction** using keyword extraction + ML models
-  **Interactive Frontend Dashboard** with expandable result cards, live analysis, and downloadable reports
-  Modular design with FastAPI, enabling scalability and API-first development
-  **Docker-based Deployment** ready for cloud or local setups



##  Project Structure

```text
cti-nlp-system/
│
├── backend/                  # FastAPI backend logic (main.py, NER, ML models)
│   ├── main.py
│   ├── threat_ner.py
│   ├── classifier.py
│   ├── severity_predictor.py
│   └── ...
│
├── dashboard/                # Frontend templates (HTML + CSS + Jinja2/JS)
│   ├── templates/
│   ├── static/
│   └── ...
│
├── data/                     # Raw and processed threat intel datasets
│   ├── raw/
│   ├── cleaned/
│   └── ...
│
├── docs/                     #  Documentation and testing guidelines
│   ├── setup_guide.md
│   ├── testing_guide.md
│   └── api_schema.json
│
├── models/                   # Saved ML models, vectorizers (joblib/pkl files)
│
├── scripts/                  # Preprocessing, training scripts for models
│   ├── train_threat_classifier.py
│   ├── preprocess.py
│   └── ...
│
├── utils/                    # Helper utilities (tokenizer, logger, metrics)
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── CONTRIBUTING.md
````



##  Technology Stack

| Category     | Tools & Libraries                                   |
| ------------ | --------------------------------------------------- |
| Backend      | **FastAPI**, Uvicorn                                |
| NLP Models   | spaCy, HuggingFace Transformers (BERT, ThreatBERT)  |
| ML Libraries | Scikit-learn, XGBoost, PyTorch                      |
| Frontend     | HTML, Bootstrap 5, JavaScript, Jinja2               |
| Dashboard    | Custom Flask/Static Pages (migrating to React/Vite) |
| Deployment   | Docker, Render, Railway                             |
| Storage      | CSV, JSON                                           |


##  Getting Started

###  1. Clone the Repository

```bash
git clone https://github.com/sanjanb/cti-nlp-system.git
cd cti-nlp-system
```

### 2. Set Up Environment

```bash
python -m venv myenv
# Windows
myenv\Scripts\activate
# Linux/Mac
source myenv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

###  3. Start the FastAPI Server

```bash
uvicorn backend.main:app --reload
```

Access the API at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

##  Testing the Application

Check the [ docs/testing\_guide.md](docs/testing_guide.md) file for full testing procedures.

### Example API Usage

```bash
curl -X POST http://localhost:8000/analyze \
    -H "Content-Type: application/json" \
    -d '{"text": "QakBot malware exploited CVE-2023-1234 via phishing in Russia"}'
```

Expected JSON:

```json
{
  "original_text": "...",
  "entities": [...],
  "threat_type": "Phishing",
  "severity": "High"
}
```

You can also upload `.csv` files with a `text` column at `/upload_csv`.



##  Documentation

| File                                             | Description                               |
| ------------------------------------------------ | ----------------------------------------- |
| [`docs/setup_guide.md`](docs/setup_guide.md)     | End-to-end setup and deployment steps     |
| [`docs/testing_guide.md`](docs/testing_guide.md) | Manual and automated testing instructions |
| [`docs/api_schema.json`](docs/api_schema.json)   | Swagger/OpenAPI schema                    |
| [`CONTRIBUTING.md`](CONTRIBUTING.md)             | Contribution guidelines                   |



##  Contributing

We welcome contributions from students, researchers, and cybersecurity enthusiasts.

>  For setup, conventions, and pull request flow, read [`CONTRIBUTING.md`](CONTRIBUTING.md).


## License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE) for more details.


## Maintainers

Developed as part of the final year project (CSE - AI & ML) at **ATME College of Engineering**, Mysuru:

* **Kushal S M**
* **Sanjan B M**
* **Ponnanna K V**
* **Vishnu S**
* *Guided by Prof. Khateeja Ambreen*

For questions or suggestions, open a GitHub issue or reach out on [LinkedIn](https://www.linkedin.com/in/sanjanb/).
