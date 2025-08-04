from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import pandas as pd
import tempfile
import json
import os
import numpy as np  # Required for sanitizing NumPy types

from threat_ner import extract_threat_entities
from classifier import classify_threat
from severity_predictor import predict_severity

app = Flask(__name__, template_folder="../dashboard/templates")
CORS(app)

def sanitize_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    else:
        return obj

@app.route("/")
def index():
    return "CTI-NLP backend running."

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

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

        response = {
            "original_text": text,
            "entities": sanitize_for_json(entities),
            "threat_type": str(threat_type),
            "severity": str(severity)
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        df = pd.read_csv(file)
        if "text" not in df.columns:
            return jsonify({"error": "CSV must contain a 'text' column"}), 400

        results = []

        for _, row in df.iterrows():
            text = row["text"]
            if not isinstance(text, str): continue

            entities = extract_threat_entities(text)
            threat_type = classify_threat(text)
            severity = predict_severity(text)

            results.append(sanitize_for_json({
                "original_text": text,
                "entities": entities,
                "threat_type": threat_type,
                "severity": severity
            }))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            file_path = f.name

        return send_file(file_path, as_attachment=True, download_name="cti_batch_results.json")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
