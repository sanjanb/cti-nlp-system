import joblib
import os

vectorizer_path = os.path.join("..", "models", "tfidf_vectorizer.pkl")
classifier_path = os.path.join("..", "models", "threat_classifier.pkl")


tfidf_vectorizer = joblib.load(vectorizer_path)
classifier_model = joblib.load(model_path)

def classify_threat(text):
    try:
        X = tfidf_vectorizer.transform([text])
        prediction = classifier_model.predict(X)[0]
        return prediction
    except Exception as e:
        return f"Classification Error: {str(e)}"
