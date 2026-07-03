import ollama
import json
import logging
import traceback
import os
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LocalVLMPipeline:
    """Powerful-Local mode: uses Typhoon OCR via Ollama for Thai bank slip extraction."""
    
    def __init__(self, model_name=None):
        self.model = model_name or os.getenv("LOCAL_VLM_MODEL", "scb10x/typhoon-ocr-3b")
        self.llm_model = os.getenv("LOCAL_LLM_MODEL", "scb10x/llama3.1-typhoon2-8b-instruct")
        logging.info(f"Initializing LocalVLMPipeline with VLM: {self.model} and LLM: {self.llm_model}")
        
    PROMPT = """Extract from this Thai bank payment slip image:
- date: the transaction date (DD MMM YYYY format)  
- receiver: the receiver/merchant name
- amount: the transaction amount (number only, no currency symbol)
- category: classify as one of [Dining, Groceries, Transport, Credit Card Settlement, Personal Transfer, Utilities, General Expense]

Return ONLY a JSON object like:
{"date": "...", "receiver": "...", "amount": 123.45, "category": "..."}
If there are multiple transactions, return a JSON array."""

    def extract_with_llm(self, raw_text: str) -> dict:
        llm_prompt = f"""
You are a data extractor. Extract the following information from the OCR text of a Thai bank slip:
- date: the transaction date (DD MMM YYYY format)  
- receiver: the receiver/merchant name
- amount: the transaction amount (number only, no currency symbol)
- category: classify as one of [Dining, Groceries, Transport, Credit Card Settlement, Personal Transfer, Utilities, General Expense]

OCR Text:
\"\"\"
{raw_text}
\"\"\"

Return ONLY a JSON object like:
{{"date": "...", "receiver": "...", "amount": 123.45, "category": "..."}}
"""
        try:
            logging.info(f"Extracting JSON from raw OCR text using LLM: {self.llm_model}")
            response = ollama.chat(
                model=self.llm_model,
                messages=[{"role": "user", "content": llm_prompt}],
                format="json"
            )
            content = response.get("message", {}).get("content", "")
            return json.loads(content)
        except Exception as e:
            logging.error(f"Error extracting with LLM: {e}")
            return {}

    def process_image(self, image_path: str) -> list[dict]:
        try:
            logging.info(f"Extracting text via VLM from {image_path}")
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            response = ollama.chat(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": self.PROMPT,
                    "images": [image_bytes]
                }],
                format="json"
            )
            
            content = response.get("message", {}).get("content", "")
            
            if not content:
                logging.error("VLM returned empty content.")
                return []
                
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If the VLM didn't return valid JSON, try to extract with LLM
                result = self.extract_with_llm(content)
            
            # If the VLM returned {"text": "raw OCR text"} (like typhoon-ocr-3b), use LLM to extract JSON
            if isinstance(result, dict) and "text" in result and "amount" not in result:
                raw_text = result["text"]
                extracted_json = self.extract_with_llm(raw_text)
                if extracted_json:
                    result = extracted_json
                    
            # Normalize to list
            if isinstance(result, dict):
                result = [result]
                
            # Normalize output structure to match the frontend expectations
            normalized_results = []
            for item in result:
                amount_val = item.get("amount", 0.0)
                if amount_val is None:
                    amount_val = 0.0
                if isinstance(amount_val, str):
                    try:
                        amount_val = float(amount_val.replace(",", "").replace("บาท", "").strip())
                    except ValueError:
                        amount_val = 0.0
                        
                normalized = {
                    "amount": float(amount_val),
                    "date": item.get("date", ""),
                    "receiver": item.get("receiver", ""),
                    "category": item.get("category", "Uncategorized"),
                    "debug_info": {"raw_texts": [content]}
                }
                normalized_results.append(normalized)
            
            return normalized_results
            
        except Exception as e:
            logging.error(f"Error processing image {image_path} via VLM: {e}")
            logging.error(traceback.format_exc())
            return None
