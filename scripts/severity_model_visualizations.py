import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
import os

# Severity Model Visualizations
os.makedirs('assets/review1', exist_ok=True)
df = pd.read_csv('data/Cybersecurity_Dataset.csv')
df = df.rename(columns=lambda x: x.strip())
text_col = 'Cleaned Threat Description'
label_col = 'Severity Score'

vectorizer = joblib.load('models/severity_vectorizer.pkl')
clf = joblib.load('models/severity_model.pkl')


y_pred = [str(x) for x in y_pred]

# Prepare test set and map all labels to string for consistency
_, X_test, _, y_test = train_test_split(df[text_col], df[label_col], test_size=0.2, random_state=42)
X_test_vec = vectorizer.transform(X_test)
y_test = y_test.astype(str)
preds = clf.predict(X_test_vec)
y_pred = [str(x) for x in preds]

# Classification report
report = classification_report(y_test, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()
report_df.to_csv('assets/review1/severity_model_metrics.csv')

# F1-score plot
plt.figure(figsize=(6,4))
report_df.loc[report_df.index != 'accuracy', 'f1-score'].plot(kind='bar', color='salmon')
plt.title('F1-score by Severity Class')
plt.ylabel('F1-score')
plt.tight_layout()
plt.savefig('assets/review1/severity_f1.png')
plt.close()

# Confusion matrix
ConfusionMatrixDisplay.from_estimator(clf, X_test_vec, y_test, cmap='Oranges', xticks_rotation=45)
plt.title('Confusion Matrix - Severity Model')
plt.tight_layout()
plt.savefig('assets/review1/severity_cm.png')
plt.close()

print('Saved severity model visualizations to assets/review1/')
