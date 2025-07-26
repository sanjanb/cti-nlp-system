# Contributing to AI-Based CTI-NLP System

This document outlines the standards and steps to follow when contributing to the **AI-Based Predictive Cyber Threat Intelligence System**. Please review the instructions carefully to maintain consistency and ensure smooth collaboration.



## Project Structure

```

cti-nlp-system/
├── backend/             # Flask backend + NLP/ML pipeline
├── dashboard/           # Frontend (HTML + Flask templates)
├── data/                # Raw and processed threat data
├── models/              # Saved models and vectorizers
├── scripts/             # Preprocessing, training, scraping scripts
├── utils/               # Helper functions and modules
├── Dockerfile           # For containerized deployment
├── docker-compose.yml   # (optional) Service orchestration
├── requirements.txt     # Python dependencies
└── README.md            # Project overview and setup guide

````



## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/cti-nlp-system.git
cd cti-nlp-system
````

### 2. Set Up a Virtual Environment

```bash
python -m venv env
source env/bin/activate      # Linux/Mac
# OR
env\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## Data Preprocessing

Add raw `.txt` files to the `data/raw/` directory.

To run the preprocessing pipeline:

```bash
python scripts/preprocess.py
```

Output will be saved in `data/processed/preprocessed_data.csv`.

---

## Running the Flask Backend

To start the API server locally:

```bash
python backend/app.py
```

---

## Contribution Workflow

Follow this workflow to contribute features, bug fixes, or documentation:

1. Create a new branch:

```bash
git checkout -b feat/your-feature-name
```

2. Add your code to the relevant module:

   * Preprocessing: `scripts/`
   * Backend/ML logic: `backend/`
   * Utilities: `utils/`
   * Frontend: `dashboard/`

3. Test your code thoroughly.

4. Commit and push your changes:

```bash
git add .
git commit -m "Add: [short description of changes]"
git push origin feat/your-feature-name
```

5. Open a Pull Request on GitHub and request a review.

---

## Dependency Management

All Python packages must be listed in `requirements.txt`.

If you install any new packages, run the following command to update the file:

```bash
pip freeze > requirements.txt
```

---

## Code Style Guidelines

* Follow PEP8 standards for Python code.
* Use `snake_case` for function and variable names.
* Write meaningful commit messages.
* Add docstrings and inline comments where necessary.
* Avoid hardcoding paths; use `Path()` or `os` modules.



## Suggestions for Contribution

* Build or improve preprocessing and scraping tools.
* Enhance entity recognition using advanced models.
* Implement additional ML pipelines for classification or severity.
* Build Flask API routes and integrate with frontend.
* Design clean and responsive HTML templates.
* Add threat intelligence samples to `data/raw/`.



## Support

For any questions or issues:

* Reach out to the project maintainers via GitHub Issues.
* Or communicate through the team discussion channel.

Thank you for your contribution and collaboration.

