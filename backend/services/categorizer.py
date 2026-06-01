import json
import os
import re
import logging
from thefuzz import process
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class Categorizer:
    def __init__(self, config_path="config/categories.json"):
        # Resolve path relative to this file to support running from anywhere
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.full_config_path = os.path.join(base_dir, config_path)
        
        # Load environment variables from .env if present
        dotenv_path = os.path.join(base_dir, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            
        self.llm_provider = os.getenv("LLM_PROVIDER", "").lower().strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        self.load_categories()

    def load_categories(self):
        with open(self.full_config_path, "r", encoding="utf-8") as f:
            self.categories = json.load(f)
        self.merchants = list(self.categories.keys())

    def get_all_mappings(self):
        return self.categories

    def update_mapping(self, receiver_name, category):
        if not receiver_name:
            return False
            
        self.categories[receiver_name] = category
        self.save_categories()
        return True

    def delete_mapping(self, receiver_name):
        if receiver_name in self.categories:
            del self.categories[receiver_name]
            self.save_categories()
            return True
        return False

    def save_categories(self):
        with open(self.full_config_path, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, indent=2, ensure_ascii=False)
        self.load_categories()

    def _local_heuristics(self, receiver_name):
        """
        Applies local rule-based keyword / regex matching to determine category.
        Returns a category string, or None if no rules match.
        """
        name_lower = receiver_name.lower().strip()
        
        # 1. Personal Transfers
        personal_prefixes = ["นาย", "นาง", "น.ส.", "นางสาว", "เด็กชาย", "เด็กหญิง", "mr.", "mrs.", "ms.", "miss", "dr."]
        for prefix in personal_prefixes:
            if name_lower.startswith(prefix):
                return "Personal Transfer"
                
        # 2-word or 3-word Thai/English names without merchant keywords or digits
        words = receiver_name.split()
        if 2 <= len(words) <= 3:
            is_valid_name = True
            for word in words:
                word_clean = word.replace(".", "")
                if not re.match(r'^[a-zA-Z\u0e00-\u0e7f]+$', word_clean):
                    is_valid_name = False
                    break
            
            merchant_keywords = ["ร้าน", "บริษัท", "บจก", "หจก", "co", "ltd", "cafe", "coffee", "store", "shop", "supermarket", "mart", "market"]
            for keyword in merchant_keywords:
                if keyword in name_lower:
                    is_valid_name = False
                    break
            
            if is_valid_name:
                return "Personal Transfer"

        # 2. Dining
        dining_keywords = [
            "restaurant", "cafe", "coffee", "bakery", "kitchen", "shabu", "sushi", "grill", "food", "boba", "tea", "bistro", "eatery",
            "ร้านอาหาร", "ครัว", "โภชนา", "หมูกระทะ", "ชาบู", "กาแฟ", "ชา", "เบเกอรี่", "ส้มตำ", "ก๋วยเตี๋ยว", "อาหาร", "กะเพรา", "สุกี้",
            "suki", "teenoi", "kfc", "mcdonald", "starbucks", "pizza"
        ]
        for keyword in dining_keywords:
            if keyword in name_lower:
                return "Dining"

        # 3. Groceries
        groceries_keywords = [
            "supermarket", "mart", "store", "shop", "grocery", "minimart", "7-eleven", "lotus", "tops", "makro", "bigc", "cj",
            "ห้าง", "มาร์ท", "ร้านค้า", "ตลาด", "ชำ", "โชห่วย"
        ]
        for keyword in groceries_keywords:
            if keyword in name_lower:
                return "Groceries"

        # 4. Transport
        transport_keywords = [
            "express", "delivery", "taxi", "car", "bts", "mrt", "gas", "petrol", "ptt", "shell", "esso", "caltex", "bangchak", "mobil",
            "เติมน้ำมัน", "ปั๊มน้ำมัน", "ขนส่ง", "วิน", "รถเมล์", "ทางด่วน", "การทางพิเศษ", "grab", "lineman", "foodpanda", "bolt"
        ]
        for keyword in transport_keywords:
            if keyword in name_lower:
                return "Transport"
                
        # 5. Utilities/Bills
        utilities_keywords = [
            "mwa", "pea", "mea", "ais", "true", "dtac", "3bb", "telecom",
            "การไฟฟ้า", "การประปา", "อินเทอร์เน็ต", "โทรศัพท์"
        ]
        for keyword in utilities_keywords:
            if keyword in name_lower:
                return "Utilities"

        # 6. Credit Card / Financial Settlements
        financial_keywords = [
            "ktc", "krungsri", "scb", "kbank", "bbl", "ttb", "uob", "citi", "aeon", "บัตรเครดิต", "ชำระเงินกู้"
        ]
        for keyword in financial_keywords:
            if keyword in name_lower:
                return "Credit Card Settlement"
                
        return None

    def _categorize_via_llm(self, receiver_name):
        prompt = f"""
You are a financial assistant that categorizes bank transfer receiver names from payment slips.
Classify the following receiver name into EXACTLY one of these categories:
- Dining
- Groceries
- Transport
- Credit Card Settlement
- Personal Transfer
- Utilities
- General Expense

Receiver Name: "{receiver_name}"

Return ONLY the category name from the list above. Do not include any punctuation, quotes, or explanatory text.
"""
        
        if self.llm_provider == "gemini" and self.gemini_key:
            if genai is None:
                logging.error("google-genai library is not installed.")
                return None
            try:
                logging.info(f"Calling Gemini API to categorize: {receiver_name}")
                client = genai.Client(api_key=self.gemini_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                category = response.text.strip()
                category = re.sub(r'[`"\']', '', category).strip()
                
                allowed_categories = ["Dining", "Groceries", "Transport", "Credit Card Settlement", "Personal Transfer", "Utilities", "General Expense"]
                for allowed in allowed_categories:
                    if category.lower() == allowed.lower():
                        return allowed
            except Exception as e:
                logging.error(f"Gemini API call failed: {e}")
                return None
                
        elif self.llm_provider == "openai" and self.openai_key:
            if OpenAI is None:
                logging.error("openai library is not installed.")
                return None
            try:
                logging.info(f"Calling OpenAI API to categorize: {receiver_name}")
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10,
                    temperature=0.0
                )
                category = response.choices[0].message.content.strip()
                category = re.sub(r'[`"\']', '', category).strip()
                
                allowed_categories = ["Dining", "Groceries", "Transport", "Credit Card Settlement", "Personal Transfer", "Utilities", "General Expense"]
                for allowed in allowed_categories:
                    if category.lower() == allowed.lower():
                        return allowed
            except Exception as e:
                logging.error(f"OpenAI API call failed: {e}")
                return None
                
        return None

    def categorize(self, receiver_name):
        if not receiver_name:
            return "Uncategorized"
            
        # 1. Match receiver_name against known merchants (fuzzy search)
        if self.merchants:
            match, score = process.extractOne(receiver_name, self.merchants)
            if score > 70:
                return self.categories[match]
                
        # 2. Try Local Heuristics
        heuristics_category = self._local_heuristics(receiver_name)
        if heuristics_category:
            self.update_mapping(receiver_name, heuristics_category)
            return heuristics_category
            
        # 3. Try LLM (Gemini or OpenAI)
        llm_category = self._categorize_via_llm(receiver_name)
        if llm_category:
            self.update_mapping(receiver_name, llm_category)
            return llm_category
            
        return "Uncategorized"


