import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# Load the dataset
df = pd.read_csv("data/Cybersecurity_Dataset.csv")

# Clean headers
df = df.rename(columns=lambda x: x.strip())

# Rename if needed
text_col = "Cleaned Threat Description"
severity_col = "Severity Score"

# Drop rows with missing data
df = df.dropna(subset=[text_col, severity_col])

# Map numeric severity to labels
def map_severity(score):
    if score <= 2:
        return "Low"
    elif score == 3:
        return "Medium"
    else:
        return "High"

df["Severity_Label"] = df[severity_col].astype(int).apply(map_severity)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    df[text_col], df["Severity_Label"], test_size=0.2, random_state=42
)

# TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_vec, y_train)

# Evaluate
y_pred = clf.predict(X_test_vec)
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(clf, "models/severity_model.pkl")
joblib.dump(vectorizer, "models/severity_vectorizer.pkl")

print("Severity model training complete.")
