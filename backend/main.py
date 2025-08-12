# backend/main.py

import asyncio
import logging
import tempfile
import os
import json
import pandas as pd

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, timezone
from scripts.ingest_all_sources import main as ingest_all_sources_main

from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity


# -------------------
# App setup
# -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI(title="CTI-NLP API with Real-Time Ingestion")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")


# -------------------
# Background ingestion
# -------------------
async def ingestion_loop(interval_minutes=10):
    """Runs data ingestion in background every X minutes."""
    while True:
        try:
            logging.info("Running real-time ingestion...")
            # Run ingestion in a thread to avoid blocking event loop
            await asyncio.to_thread(ingest_all_sources_main)
            logging.info("Ingestion cycle completed.")
        except Exception as e:
            logging.error(f"Ingestion loop failed: {e}")
        await asyncio.sleep(interval_minutes * 60)


@app.on_event("startup")
async def startup_event():
    """Start background ingestion task."""
    asyncio.create_task(ingestion_loop(interval_minutes=10))


# -------------------
# API Routes
# -------------------
@app.get("/")
def root():
    return {
        "status": "CTI-NLP backend running with real-time ingestion",
        "last_ingestion_time": datetime.now(timezone.utc).isoformat()
    }


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
        logging.exception("Error in /analyze endpoint")
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

        return FileResponse(
            path=file_path,
            filename="cti_batch_results.json",
            media_type='application/json'
        )

    except Exception as e:
        logging.exception("Error in /upload_csv endpoint")
        return JSONResponse(status_code=500, content={"error": str(e)})
