import joblib
import os

vectorizer_path = os.path.join("models", "tfidf_vectorizer.pkl")
classifier_path = os.path.join("models", "threat_classifier.pkl")
    


tfidf_vectorizer = joblib.load(vectorizer_path)
classifier_model = joblib.load(classifier_path)

print("[INFO] TF-IDF Vectorizer and Classifier loaded successfully.")


def classify_threat(text):
    try:
        X = tfidf_vectorizer.transform([text])
        prediction = classifier_model.predict(X)[0]
        probabilities = classifier_model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        return {
            "category": prediction,
            "confidence": float(confidence)
        }
    except Exception as e:
        return {
            "category": "Other",
            "confidence": 0.0
        }
