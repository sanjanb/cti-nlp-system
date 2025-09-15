# Model Selection & Metrics Visualization Script

This script demonstrates how we compared models, calculated metrics, and generated visualizations for our project review. Save this as `scripts/model_selection_metrics.py` and run after training your models.

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import joblib

# Load test data
# (Assume same split as in training scripts)
df = pd.read_csv("data/Cybersecurity_Dataset.csv")
df = df.rename(columns=lambda x: x.strip())
text_col = "Cleaned Threat Description"
label_col = "Threat Category"

# Load models
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
clf = joblib.load("models/threat_classifier.pkl")

# Prepare test set (simulate split)
from sklearn.model_selection import train_test_split
_, X_test, _, y_test = train_test_split(
    df[text_col], df[label_col], test_size=0.2, random_state=42
)
X_test_tfidf = vectorizer.transform(X_test)

# Predict
y_pred = clf.predict(X_test_tfidf)

# Classification report
report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# Save metrics table
report_df.to_csv("assets/review1/threat_classifier_metrics.csv")

# Plot F1-score for each class
plt.figure(figsize=(8,4))
report_df.loc[report_df.index != 'accuracy', 'f1-score'].plot(kind='bar', color='skyblue')
plt.title('F1-score by Threat Category')
plt.ylabel('F1-score')
plt.tight_layout()
plt.savefig('assets/review1/threat_classifier_f1.png')
plt.close()

# Confusion matrix
ConfusionMatrixDisplay.from_estimator(clf, X_test_tfidf, y_test, cmap='Blues', xticks_rotation=45)
plt.title('Confusion Matrix - Threat Classifier')
plt.tight_layout()
plt.savefig('assets/review1/threat_classifier_cm.png')
plt.close()

print("Saved metrics and visualizations to assets/review1/")
```

- Run this script after training to generate the metrics and visualizations for your presentation.
- Repeat similar steps for severity and NER models as needed.
