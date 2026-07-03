import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import shutil

from services.ocr_parser import SlipParser
from services.categorizer import Categorizer
from services.processor_factory import ProcessorFactory

app = FastAPI(title="Slip OCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
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
        mode = os.getenv("PROCESSING_MODE", "lite")
        processor = ProcessorFactory.get(mode)
        parsed_records = processor.process_image(file_path)
        
        if parsed_records is not None:
            for record in parsed_records:
                # If processor didn't assign category (like Lite mode), use categorizer
                if "category" not in record or record["category"] == "Uncategorized" or not record["category"]:
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

class CategoryUpdate(BaseModel):
    receiver: str
    category: str

@app.get("/categories/")
async def get_categories():
    return categorizer.get_all_mappings()

@app.post("/update-category/")
async def update_category(data: CategoryUpdate):
    success = categorizer.update_mapping(data.receiver, data.category)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid receiver name")
    return {"status": "success"}

@app.delete("/categories/")
async def delete_category(receiver: str):
    success = categorizer.delete_mapping(receiver)
    if not success:
        raise HTTPException(status_code=404, detail="Receiver mapping not found")
    return {"status": "success"}

class SettingsUpdate(BaseModel):
    processing_mode: str = None
    llm_provider: str = None

@app.get("/settings/")
async def get_settings():
    return {
        "processing_mode": os.getenv("PROCESSING_MODE", "lite"),
        "llm_provider": os.getenv("LLM_PROVIDER", "local")
    }

@app.post("/settings/")
async def update_settings(data: SettingsUpdate):
    if data.processing_mode:
        os.environ["PROCESSING_MODE"] = data.processing_mode
    if data.llm_provider:
        os.environ["LLM_PROVIDER"] = data.llm_provider
        categorizer.llm_provider = data.llm_provider
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

