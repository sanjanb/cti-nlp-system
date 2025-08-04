from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import tempfile
import os
import json

from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity


app = FastAPI(title="CTI-NLP API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")


@app.get("/")
def root():
    return {"message": "CTI-NLP backend running."}


@app.get("/dashboard")
def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_text(payload: dict):
    text = payload.get("text", "")
    if not text:
        return JSONResponse(status_code=400, content={"error": "No input text provided."})

    try:
        entities = extract_threat_entities(text)
        threat_type = classify_threat(text)
        severity = predict_severity(text)

        return {
            "original_text": text,
            "entities": entities,
            "threat_type": str(threat_type),
            "severity": str(severity),
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        if "text" not in df.columns:
            return JSONResponse(status_code=400, content={"error": "CSV must contain a 'text' column"})

        results = []

        for _, row in df.iterrows():
            text = row["text"]
            if not isinstance(text, str):
                continue

            entities = extract_threat_entities(text)
            threat_type = classify_threat(text)
            severity = predict_severity(text)

            results.append({
                "original_text": text,
                "entities": entities,
                "threat_type": str(threat_type),
                "severity": str(severity),
            })

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            file_path = f.name

        return FileResponse(path=file_path, filename="cti_batch_results.json", media_type='application/json')

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
