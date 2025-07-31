import joblib

# Load models
severity_vectorizer = joblib.load("models/severity_vectorizer.pkl")
severity_model = joblib.load("models/severity_model.pkl")

def predict_severity(text):
    features = severity_vectorizer.transform([text])
    prediction = severity_model.predict(features)
    return prediction[0]
