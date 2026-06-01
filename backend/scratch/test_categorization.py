import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.categorizer import Categorizer

def test_categorization():
    print("=== Starting Categorization Test ===")
    
    # 1. Create a temp test categories config
    temp_config = "config/test_categories.json"
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_temp_path = os.path.join(base_dir, temp_config)
    os.makedirs(os.path.dirname(full_temp_path), exist_ok=True)
    
    test_data = {
        "TOPS": "Groceries",
        "KFC": "Dining"
    }
    
    with open(full_temp_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
        
    try:
        # Initialize categorizer with temp config
        categorizer = Categorizer(config_path=temp_config)
        
        # Test Case 1: Fuzzy match
        print("\nTest Case 1: Fuzzy matching with known merchants...")
        res = categorizer.categorize("Tops Supermarket")
        print(f"Input: 'Tops Supermarket' -> Output: '{res}' (Expected: 'Groceries')")
        assert res == "Groceries", "Fuzzy match failed"
        
        # Test Case 2: Heuristics - Personal Prefix
        print("\nTest Case 2: Heuristics - Personal Prefix (Thai)...")
        res = categorizer.categorize("นาย สมศักดิ์ รักดี")
        print(f"Input: 'นาย สมศักดิ์ รักดี' -> Output: '{res}' (Expected: 'Personal Transfer')")
        assert res == "Personal Transfer", "Personal prefix heuristics failed"
        
        # Test Case 3: Heuristics - English Prefix
        print("\nTest Case 3: Heuristics - Personal Prefix (English)...")
        res = categorizer.categorize("Mr. John Doe")
        print(f"Input: 'Mr. John Doe' -> Output: '{res}' (Expected: 'Personal Transfer')")
        assert res == "Personal Transfer", "Personal prefix heuristics failed"

        # Test Case 4: Heuristics - 2-word Thai Name (P2P)
        print("\nTest Case 4: Heuristics - 2-word Personal Name...")
        res = categorizer.categorize("สมศรี สุขใจ")
        print(f"Input: 'สมศรี สุขใจ' -> Output: '{res}' (Expected: 'Personal Transfer')")
        assert res == "Personal Transfer", "2-word personal name heuristics failed"
        
        # Test Case 5: Heuristics - Dining
        print("\nTest Case 5: Heuristics - Dining...")
        res = categorizer.categorize("ครัวคุณต๋อย")
        print(f"Input: 'ครัวคุณต๋อย' -> Output: '{res}' (Expected: 'Dining')")
        assert res == "Dining", "Dining heuristics failed"

        # Test Case 6: Heuristics - Groceries
        print("\nTest Case 6: Heuristics - Groceries...")
        res = categorizer.categorize("ร้านโชห่วยเจ๊แดง")
        print(f"Input: 'ร้านโชห่วยเจ๊แดง' -> Output: '{res}' (Expected: 'Groceries')")
        assert res == "Groceries", "Groceries heuristics failed"
        
        # Test Case 7: Heuristics - Transport
        print("\nTest Case 7: Heuristics - Transport...")
        res = categorizer.categorize("วินมอเตอร์ไซค์")
        print(f"Input: 'วินมอเตอร์ไซค์' -> Output: '{res}' (Expected: 'Transport')")
        assert res == "Transport", "Transport heuristics failed"
        
        print("\n=== All Local Heuristics Tests Passed! ===")
        
        # Check if LLM is configured
        if categorizer.llm_provider and (categorizer.gemini_key or categorizer.openai_key):
            print(f"\nTest Case 8: LLM Categorization ({categorizer.llm_provider.upper()})...")
            res = categorizer.categorize("โรงพยาบาลศิริราช")
            print(f"Input: 'โรงพยาบาลศิริราช' -> Output: '{res}'")
            print(f"Learned mappings updated: {categorizer.categories}")
        else:
            print("\nLLM API not configured, skipping LLM test cases.")
            
    finally:
        # Clean up test categories file
        if os.path.exists(full_temp_path):
            os.remove(full_temp_path)

if __name__ == "__main__":
    test_categorization()
