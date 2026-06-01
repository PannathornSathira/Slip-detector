import json
import os
from thefuzz import process

class Categorizer:
    def __init__(self, config_path="config/categories.json"):
        # Resolve path relative to this file to support running from anywhere
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.full_config_path = os.path.join(base_dir, config_path)
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

    def categorize(self, receiver_name):
        if not receiver_name or not self.merchants:
            return "Uncategorized"
            
        # Match receiver_name against known merchants
        match, score = process.extractOne(receiver_name, self.merchants)
        
        # If confidence is > 70, consider it a match
        if score > 70:
            return self.categories[match]
            
        return "Uncategorized"

