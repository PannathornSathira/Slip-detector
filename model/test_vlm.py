import ollama
import sys
import json
import time

def test_model(model_name, image_path):
    print(f"\n{'='*50}")
    print(f"Testing model: {model_name}")
    print(f"{'='*50}")
    
    prompt = """Extract from this Thai bank payment slip image:
- date: the transaction date (DD MMM YYYY format)  
- receiver: the receiver/merchant name
- amount: the transaction amount (number only, no currency symbol)
- category: classify as one of [Dining, Groceries, Transport, Credit Card Settlement, Personal Transfer, Utilities, General Expense]

Return ONLY a JSON object like:
{"date": "...", "receiver": "...", "amount": 123.45, "category": "..."}
If there are multiple transactions, return a JSON array."""

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        start_time = time.time()
        print("Sending request to Ollama...")
        
        # Note: We are not enforcing format="json" here so we can see 
        # exactly what the model naturally outputs if it fails to format properly.
        response = ollama.chat(
            model=model_name,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_bytes]
            }]
        )
        
        end_time = time.time()
        
        content = response.get("message", {}).get("content", "")
        print(f"\n[Time taken: {end_time - start_time:.2f} seconds]")
        print("\n--- RAW RESPONSE ---")
        print(content)
        print("--------------------")
        
        try:
            # Simple cleanup to help parse if it returned markdown JSON block
            clean_content = content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            if clean_content.startswith("```"):
                clean_content = clean_content[3:]
            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]
                
            parsed = json.loads(clean_content.strip())
            print("\n✅ Successfully parsed as JSON:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("\n❌ Failed to parse response as JSON.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_vlm.py <path_to_image>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    # Test the large Typhoon OCR model first
    test_model("scb10x/typhoon-ocr-3b", image_path)
    
    # Then test the smaller MiniCPM-V model
    #test_model("minicpm-v:latest", image_path)
