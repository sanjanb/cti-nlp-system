![header](assets/header.png)

# AI-Based Predictive Cyber Threat Intelligence System Using NLP

This project is an intelligent Cyber Threat Intelligence (CTI) platform that leverages Natural Language Processing (NLP) and Anomaly Detection techniques to analyze unstructured threat data, extract meaningful indicators, classify threat types, predict severity levels, and present the insights through a web-based interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

In an era of rapidly evolving cyber threats, traditional rule-based systems fall short in delivering real-time intelligence. This project aims to build a predictive CTI system that automates threat analysis using NLP techniques and AI-based classification models. It extracts threat entities (e.g., malware names, CVEs, IP addresses), categorizes threat types (e.g., phishing, ransomware), predicts severity, and presents the results on an accessible dashboard.

## Features

- Extraction of Indicators of Compromise (IOCs) using Named Entity Recognition (NER)
- Classification of threats into categories such as Phishing, Malware, and APTs
- Severity prediction using NLP keyword indicators and behavioral anomaly detection
- Dashboard visualization using Flask with basic filtering and search
- Modular architecture and Docker-based deployment for ease of setup

## Project Structure

```

cti-nlp-system/
├── backend/             # Flask backend + NLP/ML pipeline
├── dashboard/           # Frontend templates (HTML + Jinja)
├── data/                # Raw and processed datasets
├── models/              # Saved models and vectorizers
├── scripts/             # Data scraping, preprocessing, training
├── utils/               # Reusable utilities
├── Dockerfile           # Docker build script
├── docker-compose.yml   # (Optional) Service orchestration
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── CONTRIBUTING.md      # Contribution guidelines

```

---

## Technology Stack

| Category      | Technologies                              |
| ------------- | ----------------------------------------- |
| Language      | Python 3.10+                              |
| NLP Models    | spaCy, BERT, ThreatBERT (via HuggingFace) |
| ML Libraries  | Scikit-learn, XGBoost, PyTorch            |
| Web Framework | Flask                                     |
| Frontend      | HTML, Bootstrap, Jinja                    |
| Deployment    | Docker                                    |
| Storage       | CSV, JSON                                 |

## Getting Started

### Prerequisites

- Python 3.10 or later
- `pip` (Python package manager)
- Docker (optional, for containerized deployment)

### Clone the Repository

```bash
git clone https://github.com/your-username/cti-nlp-system.git
cd cti-nlp-system
```

### Set Up Environment

```bash
python -m venv env
source env/bin/activate        # On Linux/Mac
# OR
env\Scripts\activate           # On Windows

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

1. Add raw `.txt` threat intelligence files to `data/raw/`.
2. Run preprocessing to generate cleaned data:

```bash
python scripts/preprocess.py
```

3. Start the Flask API server:

```bash
python backend/app.py
```

4. Access the dashboard at `http://localhost:5000`.

---

## Contributing

Please refer to the [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup instructions, branch workflow, code style, and contribution practices.

- Follow the naming conventions.
- Keep code modular and test before committing.
- Use pull requests for code review.

---

## License

This project is licensed under the [MIT License](./LICENSE).

---

## Maintainers

This project is developed by students from the Department of CSE (AI & ML), ATMECE Mysuru.

- Kushal S M
- Sanjan B M
- Ponnanna K V
- Vishnu S
- Guided by Prof. Khateeja Ambreen

---

For questions or issues, please open a GitHub issue or contact the maintainers.
