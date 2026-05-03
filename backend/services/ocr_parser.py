import easyocr
import re
import logging
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SlipParser:
    ANCHOR_KEYWORDS = ["ไปยัง", "รายการโอน", "ถุงเงิน", "ผู้รับ", "รับเงิน", "TOPS", "ร้านค้า"]

    def __init__(self):
        logging.info("Initializing EasyOCR...")
        self.reader = easyocr.Reader(['th', 'en'])

    def normalize_year(self, year_str):
        if not year_str:
            return None
        year = int(year_str)
        if year < 100:
            # Assume 2-digit Buddhist year (e.g., 69 -> 2569)
            year += 2500
        if year > 2400:
            # Convert Buddhist to Gregorian
            return year - 543
        return year

    def parse_amounts(self, texts):
        # Look for numbers with commas and decimals, possibly negative, with or without currency
        amount_pattern = re.compile(r"(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))")
        
        amounts = []
        for text in texts:
            matches = amount_pattern.findall(text)
            for m in matches:
                try:
                    val = float(m.replace(",", ""))
                    val = abs(val) # Normalize to positive
                    if val > 0 and val not in amounts:
                        amounts.append(val)
                except ValueError:
                    pass
        
        if not amounts:
            return [0.0]
            
        # Return all unique non-zero amounts found
        return amounts

    def parse_date(self, texts):
        # Very simplistic regex for date matching (DD/MM/YYYY, or Thai format like 22 เม.ย. 69)
        # We will try to extract just the year to normalize it
        year_pattern = re.compile(r"25\d{2}|20\d{2}|\b[6-9]\d\b")
        date_pattern = re.compile(r"(\d{1,2}\s+(?:ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})", re.IGNORECASE)

        extracted_date = "Unknown Date"
        normalized_year = None

        for text in texts:
            date_match = date_pattern.search(text)
            if date_match:
                extracted_date = date_match.group(1)
                
                # Try to find year in this string
                year_match = year_pattern.search(extracted_date)
                if year_match:
                    normalized_year = self.normalize_year(year_match.group(0))
                break

        return extracted_date, normalized_year

    def parse_receiver(self, texts):
        for i, text in enumerate(texts):
            # 1. Check if the text itself matches an anchor keyword or contains it
            for anchor in self.ANCHOR_KEYWORDS:
                if anchor in text:
                    # Heuristic: the receiver is often the current line (if it has more than just the anchor)
                    # or the next line.
                    clean_text = text.replace(anchor, "").strip()
                    if clean_text:
                        return clean_text
                    elif i + 1 < len(texts):
                        return texts[i + 1]

        # 2. If no anchor found, try finding generic merchant names or fallback
        # Often, lines with MR., MISS, น.ส., นาย are receivers
        name_prefixes = ["นาย", "นาง", "น.ส.", "MR.", "MISS", "MS.", "บจก", "บริษัท"]
        for text in texts:
            for prefix in name_prefixes:
                if text.startswith(prefix):
                    return text
                    
        return "Unknown Receiver"

    def process_image(self, image_path):
        try:
            logging.info(f"Extracting text from {image_path}")
            result = self.reader.readtext(image_path, detail=0) # detail=0 returns just the strings
            
            logging.info(f"Raw OCR Output: {result}")

            amounts = self.parse_amounts(result)
            date, year = self.parse_date(result)
            
            # If multiple amounts are found, we assume sub-payments and leave receiver blank
            if len(amounts) > 1:
                receiver = ""
            else:
                receiver = self.parse_receiver(result)

            debug_info = {
                "raw_texts": result
            }

            records = []
            for amount in amounts:
                records.append({
                    "amount": amount,
                    "date": date,
                    "normalized_year": year,
                    "receiver": receiver,
                    "debug_info": debug_info
                })
                
            return records
        except Exception as e:
            logging.error(f"Error processing image {image_path}: {e}")
            logging.error(traceback.format_exc())
            return None
