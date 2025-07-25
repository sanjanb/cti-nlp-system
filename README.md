# AI-Based Predictive Cyber Threat Intelligence System Using NLP

An intelligent, self-learning cyber threat intelligence (CTI) system that leverages **Natural Language Processing (NLP)** and **Artificial Immune System (AIS)** techniques to autonomously extract, analyze, classify, and predict the severity of cyber threats in real-time.

## Project Members

- **Kushal S M** – 4AD22CI024  
- **Sanjan B M** – 4AD22CI046  
- **Ponnanna K V** – 4AD22CI037  
- **Vishnu S** – 4AD23CI409  
- **Guided by:** Prof. Khateeja Ambreen, Assistant Professor, Dept. of CSE-AI & ML, ATMECE Mysuru

---

## Project Overview

With cyber threats becoming more dynamic, sophisticated, and harder to detect, traditional rule-based systems fail to keep up. This project aims to build a proactive CTI system that automates the process of:

- Extracting **Indicators of Compromise (IOCs)** from unstructured cybersecurity text
- Classifying the type of threat (e.g., phishing, malware, APTs)
- Predicting the **severity** of threats using AI models
- Visualizing the results through a user-friendly dashboard

---

## Key Features

- ✅ Automated extraction of threat entities using **NER**
- ✅ Categorization using pretrained models like **BERT / ThreatBERT**
- ✅ **Severity Prediction** (Low, Medium, High, Critical)
- ✅ **Anomaly Detection** using Artificial Immune System (AIS) concept
- ✅ Mapping to **MITRE ATT&CK** framework
- ✅ Interactive **Dashboard** using Node.js & React

---

## System Architecture

```text
[Raw Threat Data Sources]
            ↓
[NLP Preprocessing + Named Entity Recognition]
            ↓
[Threat Classification + Severity Prediction]
            ↓
[Knowledge Base + MITRE Mapping]
            ↓
[Frontend Dashboard (Node.js + React)]
````

---

## Tech Stack

| Layer        | Technologies                                              |
| ------------ | --------------------------------------------------------- |
| **NLP**      | Python, spaCy, HuggingFace Transformers, BERT, ThreatBERT |
| **ML**       | PyTorch, Scikit-learn, XGBoost                            |
| **Backend**  | Node.js, Express.js / Flask                               |
| **Frontend** | React.js, TailwindCSS, Chart.js                           |
| **Storage**  | SQLite / JSON / MongoDB (optional)                        |

---

## Installation & Setup

```bash
# Clone the repo
git clone https://github.com/your-username/cti-nlp-predictive-system.git
cd cti-nlp-predictive-system

# Backend setup (if using Python Flask)
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd ../dashboard
npm install
npm start
```

---

## Project Structure

```
cti-nlp-predictive-system/
├── backend/               # NLP/ML API code (Python/Flask or Express.js)
├── ml_model/              # Training scripts, models, preprocessing
├── dashboard/             # React frontend for visualization
├── data/                  # Sample threat text files
└── README.md              # Project documentation
```

---

## Screenshots (Coming Soon)

* Threat Classification Dashboard
* Severity Prediction Results
* IOC Entity Extraction

---

## References

* [BERT - Transformers by Hugging Face](https://huggingface.co/transformers/)
* [MITRE ATT\&CK Framework](https://attack.mitre.org/)
* [AIS Concept in Cybersecurity](https://en.wikipedia.org/wiki/Artificial_immune_system)


## Contact

Feel free to reach out for collaborations or suggestions:

**Email:** `sanjanacharaya1234@gmail.com`
**LinkedIn:** [LinkedIn](https://www.linkedin.com/in/sanjan-bm/)

---

> “Cybersecurity is not just a technology problem—it’s a people and process challenge.”
