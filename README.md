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
