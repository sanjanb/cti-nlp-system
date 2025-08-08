# train_threat_classifier_ensemble.py

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import classification_report, accuracy_score

# ===== Step 1: Load Datasets =====
train_df = pd.read_csv("data\cyber-threat-intelligence-splited_train.csv")
val_df = pd.read_csv("data\cyber-threat-intelligence-splited_validate.csv")
test_df = pd.read_csv("dat\cyber-threat-intelligence-splited_test.csv")

# Combine train + validate
train_df = pd.concat([train_df, val_df], ignore_index=True)

# Ensure no NaNs
train_df = train_df.dropna(subset=["text", "threat_type"])
test_df = test_df.dropna(subset=["text", "threat_type"])

X_train = train_df["text"]
y_train = train_df["threat_type"]
X_test = test_df["text"]
y_test = test_df["threat_type"]

# ===== Step 2: TF-IDF Feature Extraction =====
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ===== Step 3: Train Models =====
# Logistic Regression
log_reg = LogisticRegression(max_iter=300, solver="liblinear")
log_reg.fit(X_train_vec, y_train)

# XGBoost Classifier
xgb_clf = XGBClassifier(
    n_estimators=300,
    learning_rate=0.1,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="mlogloss"
)
xgb_clf.fit(X_train_vec, y_train)

# Ensemble (soft voting)
ensemble_clf = VotingClassifier(
    estimators=[
        ("log_reg", log_reg),
        ("xgb", xgb_clf)
    ],
    voting="soft"
)
ensemble_clf.fit(X_train_vec, y_train)

# ===== Step 4: Evaluate =====
models = {
    "Logistic Regression": log_reg,
    "XGBoost": xgb_clf,
    "Ensemble": ensemble_clf
}

print("\Model Comparison on Test Set\n")
results = []
for name, model in models.items():
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    results.append((name, acc))
    print(f"--- {name} ---")
    print(classification_report(y_test, y_pred))
    print("\n")

# Create a comparison table
results_df = pd.DataFrame(results, columns=["Model", "Accuracy"])
print("Accuracy Comparison:\n", results_df)

# ===== Step 5: Save Best Model (Ensemble) =====
joblib.dump(vectorizer, "models/threat_vectorizer.pkl")
joblib.dump(ensemble_clf, "models/threat_classifier.pkl")

print("\Saved ensemble model and vectorizer to 'models/'")
