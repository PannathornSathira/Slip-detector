import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil

from services.ocr_parser import SlipParser
from services.categorizer import Categorizer

app = FastAPI(title="Slip OCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
parser = SlipParser()
categorizer = Categorizer()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-slips/")
async def upload_slips(files: List[UploadFile] = File(...)):
    results = []
    
    for file in files:
        # Save temp file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Extract data (returns a list of records)
        parsed_records = parser.process_image(file_path)
        
        if parsed_records:
            for record in parsed_records:
                # Categorize based on receiver
                category = categorizer.categorize(record.get("receiver", ""))
                record["category"] = category
                record["filename"] = file.filename
                results.append(record)
        else:
            results.append({
                "filename": file.filename,
                "error": "Failed to process image."
            })
            
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    return {"data": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
