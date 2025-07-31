import joblib

# Load models
tfidf_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
classifier_model = joblib.load("models/threat_classifier.pkl")

def classify_threat(text):
    features = tfidf_vectorizer.transform([text])
    prediction = classifier_model.predict(features)
    return prediction[0]
