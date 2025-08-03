import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os

# Load the dataset
df = pd.read_csv("data/Cybersecurity_Dataset.csv")

# Check column names (modify if needed)
print("Available columns:", df.columns)

# Rename columns as needed
df = df.rename(columns=lambda x: x.strip())  # Remove accidental spaces
text_col = "Cleaned Description"
label_col = "Threat Category"

# Drop rows with missing values
df = df.dropna(subset=[text_col, label_col])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df[text_col], df[label_col], test_size=0.2, random_state=42
)

# Vectorize
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train classifier
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_tfidf, y_train)

# Evaluate
y_pred = clf.predict(X_test_tfidf)
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save models
os.makedirs("models", exist_ok=True)
joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
joblib.dump(clf, "models/threat_classifier.pkl")

print("Model training complete and files saved.")
