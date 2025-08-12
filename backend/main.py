from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from scripts.ingest_all_sources import main as ingest_all_sources_main

import asyncio
import pandas as pd
import tempfile
import os
import json

from backend.threat_ner import extract_threat_entities
from backend.classifier import classify_threat
from backend.severity_predictor import predict_severity

app = FastAPI(title="CTI-NLP API")

# -------------------
# Background ingestion
# -------------------
async def ingestion_loop(interval_minutes=10):
    while True:
        try:
            print("[INFO] Running real-time ingestion...")
            ingest_all_sources_main()
        except Exception as e:
            print(f"[ERROR] Ingestion loop failed: {e}")
        await asyncio.sleep(interval_minutes * 60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ingestion_loop(interval_minutes=10))

# -------------------
# CORS Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")

# -------------------
# Root endpoint with ingestion status
# -------------------
@app.get("/")
async def root():
    status_file = os.path.join("data", "last_ingestion.json")
    if os.path.exists(status_file):
        with open(status_file, "r", encoding="utf-8") as f:
            status_data = json.load(f)
    else:
        status_data = {
            "last_run": None,
            "summary": {},
            "total_records": 0,
            "errors": {}
        }
    return {
        "status": "CTI-NLP backend running with real-time ingestion",
        "ingestion_status": status_data
    }


@app.get("/feed")
async def get_feed(limit: int = 20):
    file_path = os.path.join("data", "ingested_cti.jsonl")
    if not os.path.exists(file_path):
        return []

    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except:
                continue

    # Return latest first
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return entries[:limit]

# -------------------
# Trigger ingestion manually
# -------------------
@app.post("/ingest_now")
async def ingest_now():
    try:
        # Run ingestion
        ingest_all_sources_main()

        # Read the updated status file
        status_file = os.path.join("data", "last_ingestion.json")
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)
        else:
            status_data = {
                "last_run": None,
                "summary": {},
                "total_records": 0,
                "errors": {}
            }

        return {
            "status": "success",
            "message": "Ingestion completed successfully",
            "ingestion_summary": status_data
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })


# -------------------
# Dashboard
# -------------------
@app.get("/dashboard")
def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------
# Analyze text
# -------------------
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

# -------------------
# Upload CSV
# -------------------
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
