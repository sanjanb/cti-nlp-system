from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity

import os

# Initialize Flask app and point to template folder
app = Flask(__name__, template_folder="../dashboard/templates")
CORS(app)

# Route to render the frontend dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# Health check route
@app.route("/")
def index():
    return "CTI-NLP backend running."

# NLP Analysis endpoint
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No input text provided."}), 400

    try:
        entities = extract_threat_entities(text)
        threat_type = classify_threat(text)
        severity = predict_severity(text)

        return jsonify({
            "original_text": text,
            "entities": entities,
            "threat_type": threat_type,
            "severity": severity
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
