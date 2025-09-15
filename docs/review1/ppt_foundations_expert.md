# CTI-NLP System: Foundations & Expert Concepts

---

## 1. Introduction to Cyber Threat Intelligence (CTI)

- **CTI** is information about threats and threat actors that helps organizations prevent or mitigate cyberattacks.
- **Why NLP for CTI?** Most threat intelligence is in unstructured text (tweets, reports, forums). NLP automates extraction and analysis.

---

## 2. Machine Learning Foundations

### Supervised Learning

- **Definition:** Training models on labeled data to predict categories or values.
- **Examples in CTI:**
  - Classifying text as 'Phishing', 'Malware', etc.
  - Predicting severity score from incident description.

### Classification Metrics

- **Accuracy:** Proportion of correct predictions.
- **Precision:** Of predicted positives, how many are correct?
- **Recall:** Of actual positives, how many did we find?
- **F1-score:** Harmonic mean of precision and recall (good for imbalanced data).
- **Confusion Matrix:** Table showing true vs. predicted classes.

---

## 3. Natural Language Processing (NLP) Pipeline

- **Text Cleaning:** Remove noise (punctuation, URLs, etc.).
- **Tokenization:** Split text into words/tokens.
- **Vectorization:** Convert text to numbers (TF-IDF, embeddings).
- **Feature Engineering:** Add custom features (keywords, n-grams, etc.).
- **Model Training:** Fit ML/DL models to features and labels.
- **Evaluation:** Use metrics to judge performance.

---

## 4. Feature Engineering in NLP

- **TF-IDF:** Measures importance of words in a document relative to the corpus.
- **Word Embeddings:** Dense vector representations (spaCy, BERT) capturing meaning/context.
- **Custom Features:**
  - Presence of threat keywords (e.g., 'CVE', 'malware')
  - N-grams (word pairs/triples)
  - Text length, sentiment

---

## 5. Model Selection: Classical vs. Deep Learning

- **Classical ML:** Logistic Regression, SVM, Random Forest, XGBoost
  - Pros: Fast, interpretable, good for small/medium data
  - Cons: May miss complex patterns
- **Deep Learning:** LSTM, BERT, DistilBERT
  - Pros: Captures context, works well on large/noisy data
  - Cons: Needs more data, compute, harder to interpret
- **Ensemble:** Combines strengths of multiple models

---

## 6. Cross-Validation & Hyperparameter Tuning

- **Cross-Validation:** Splits data into folds to test model generalizability.
- **Grid/Random Search:** Systematically try different model settings to find the best.

---

## 7. Named Entity Recognition (NER)

- **NER:** Identifies entities (e.g., malware, organizations, CVEs) in text.
- **Approaches:**
  - Rule-based (spaCy patterns)
  - ML/DL (LSTM, BERT fine-tuning)
- **Metrics:** Entity-level precision, recall, F1

---

## 8. Error Analysis & Model Robustness

- **Class Imbalance:** Some threats are rare; use F1, resampling, or class weights.
- **Noisy Text:** Misspellings, slang, and abbreviations are common in CTI.
- **Error Analysis:** Review misclassified samples to improve models.

---

## 9. Deployment & Real-World Considerations

- **API Deployment:** Use FastAPI for serving models.
- **Dockerization:** Package everything for easy deployment.
- **Monitoring:** Track model performance over time.
- **Updating Models:** Retrain as new threats/data emerge.

---

## 10. Advanced Topics (Expert Level)

- **Transfer Learning:** Use pre-trained models (BERT, DistilBERT) and fine-tune on CTI data.
- **Active Learning:** Use model uncertainty to select new samples for labeling.
- **Explainability:** Use SHAP/LIME to interpret model predictions.
- **Real-Time Ingestion:** Stream data from Twitter/APIs for live threat detection.
- **Threat Graphs:** Link entities and events for deeper analysis.

---

## 11. Further Reading & Resources

- [scikit-learn documentation](https://scikit-learn.org/stable/)
- [spaCy NLP library](https://spacy.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [FastAPI](https://fastapi.tiangolo.com/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [Awesome Threat Intelligence](https://github.com/hslatman/awesome-threat-intelligence)

---

_This document supports your understanding of all foundational and advanced concepts used in the CTI-NLP project. Use it for revision, Q&A, and deeper learning._
