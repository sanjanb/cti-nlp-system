import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
os.makedirs('assets/review1', exist_ok=True)
df = pd.read_csv('data/Cybersecurity_Dataset.csv')
df = df.rename(columns=lambda x: x.strip())

# Plot class distribution (Threat Category)
plt.figure(figsize=(8,4))
sns.countplot(y=df['Threat Category'], order=df['Threat Category'].value_counts().index, palette='viridis')
plt.title('Threat Category Distribution')
plt.xlabel('Count')
plt.ylabel('Threat Category')
plt.tight_layout()
plt.savefig('assets/review1/threat_category_distribution.png')
plt.close()

# Plot severity score distribution (if available)
if 'Severity Score' in df.columns:
    plt.figure(figsize=(6,4))
    sns.countplot(x=df['Severity Score'], palette='magma')
    plt.title('Severity Score Distribution')
    plt.xlabel('Severity Score')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('assets/review1/severity_score_distribution.png')
    plt.close()

# Plot text length distribution
plt.figure(figsize=(8,4))
df['text_length'] = df['Cleaned Threat Description'].astype(str).apply(len)
sns.histplot(df['text_length'], bins=30, kde=True, color='teal')
plt.title('Threat Description Length Distribution')
plt.xlabel('Text Length (characters)')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('assets/review1/text_length_distribution.png')
plt.close()

print('Saved dataset visualizations to assets/review1/')
