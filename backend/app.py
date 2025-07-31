from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests if needed

@app.route("/")
def index():
    return "CTI-NLP System is Running"

@app.route("/analyze", methods=["POST"])
def analyze_threat():
    data = request.get_json()
    input_text = data.get("text", "")

    if not input_text:
        return jsonify({"error": "No text provided"}), 400

    # Dummy response (replace with model logic later)
    result = {
        "original_text": input_text,
        "entities": [
            {"type": "IP", "value": "192.168.1.1"},
            {"type": "CVE", "value": "CVE-2024-1234"},
        ],
        "threat_type": "Malware",
        "severity": "High"
    }

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)
