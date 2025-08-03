import joblib
import os

# Load models
vectorizer_path = os.path.join("models", "severity_vectorizer.pkl")
model_path = os.path.join("models", "severity_model.pkl")

severity_vectorizer = joblib.load(vectorizer_path)
severity_model = joblib.load(model_path)

def predict_severity(text):
    try:
        X = severity_vectorizer.transform([text])
        prediction = severity_model.predict(X)[0]
        return prediction
    except Exception as e:
        return f"Severity Prediction Error: {str(e)}"
