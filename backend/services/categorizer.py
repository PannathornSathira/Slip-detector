import json
import os
from thefuzz import process

class Categorizer:
    def __init__(self, config_path="config/categories.json"):
        # Resolve path relative to this file to support running from anywhere
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_config_path = os.path.join(base_dir, config_path)
        
        with open(full_config_path, "r", encoding="utf-8") as f:
            self.categories = json.load(f)
            
        self.merchants = list(self.categories.keys())

    def categorize(self, receiver_name):
        if not receiver_name:
            return "Uncategorized"
            
        # Match receiver_name against known merchants
        match, score = process.extractOne(receiver_name, self.merchants)
        
        # If confidence is > 70, consider it a match
        if score > 70:
            return self.categories[match]
            
        return "Uncategorized"
