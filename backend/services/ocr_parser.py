import easyocr
import re
import logging
import traceback
from thefuzz import fuzz

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SlipParser:
    ANCHOR_KEYWORDS = ["ไปยัง", "รายการโอน", "ถุงเงิน", "ผู้รับ", "รับเงิน", "TOPS", "ร้านค้า", "โอนเงินให้"]

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

    def group_lines_by_y(self, results, y_tolerance=20):
        """
        Group bounding boxes into rows based on Y-coordinates.
        results is a list of (bbox, text, prob)
        bbox is [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        """
        lines = []
        for bbox, text, prob in results:
            # Calculate center Y of the bounding box
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_center = (bbox[0][0] + bbox[1][0]) / 2
            
            item = {
                'text': text,
                'bbox': bbox,
                'y_center': y_center,
                'x_center': x_center,
                'x1': bbox[0][0],
                'y1': bbox[0][1],
                'x2': bbox[1][0],
                'y2': bbox[2][1],
                'prob': prob
            }
            
            # Find an existing line that this item belongs to
            placed = False
            for line in lines:
                # If the Y center is within tolerance, we consider it the same line
                if abs(line['y_center'] - y_center) <= y_tolerance:
                    line['items'].append(item)
                    # Update line's average Y center
                    line['y_center'] = sum(i['y_center'] for i in line['items']) / len(line['items'])
                    placed = True
                    break
            
            if not placed:
                lines.append({
                    'y_center': y_center,
                    'items': [item]
                })
        
        # Sort lines top to bottom
        lines.sort(key=lambda l: l['y_center'])
        
        # Sort items in each line left to right
        for line in lines:
            line['items'].sort(key=lambda i: i['x_center'])
            
        return lines

    def parse_amounts(self, lines):
        # Look for numbers with commas and decimals, possibly negative, with or without currency
        amount_pattern = re.compile(r"(-?\d{1,3}(?:,\d{3})*(?:\.\d{2}))")
        
        amounts = []
        for line in lines:
            for item in line['items']:
                text = item['text']
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

    def parse_date(self, lines):
        # Very simplistic regex for date matching (DD/MM/YYYY, or Thai format like 22 เม.ย. 69)
        # We will try to extract just the year to normalize it
        year_pattern = re.compile(r"25\d{2}|20\d{2}|\b[6-9]\d\b")
        date_pattern = re.compile(r"(\d{1,2}\s+(?:ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})", re.IGNORECASE)

        extracted_date = "Unknown Date"
        normalized_year = None

        for line in lines:
            for item in line['items']:
                text = item['text']
                date_match = date_pattern.search(text)
                if date_match:
                    extracted_date = date_match.group(1)
                    
                    # Try to find year in this string
                    year_match = year_pattern.search(extracted_date)
                    if year_match:
                        normalized_year = self.normalize_year(year_match.group(0))
                    return extracted_date, normalized_year

        return extracted_date, normalized_year

    def parse_receiver(self, lines):
        # Flatten all items for spatial reasoning
        flat_items = []
        for line in lines:
            flat_items.extend(line['items'])
            
        # Sort by top-down, left-right
        flat_items.sort(key=lambda i: (i['y_center'], i['x_center']))
        
        # 1. Fuzzy match anchors
        for idx, item in enumerate(flat_items):
            text = item['text'].replace(" ", "")
            
            is_anchor = False
            for anchor in self.ANCHOR_KEYWORDS:
                # Use fuzzy match (ratio > 80 is a good match)
                if fuzz.partial_ratio(anchor, text) > 80:
                    is_anchor = True
                    # Clean the anchor from the text if it's mixed
                    clean_text = item['text']
                    for a in self.ANCHOR_KEYWORDS:
                        clean_text = clean_text.replace(a, "").strip()
                    
                    if len(clean_text) > 3: # If there's still a decent name left in the same block
                        return clean_text
                    break
            
            if is_anchor:
                # Look for the receiver in the same line (to the right) or next lines
                item_y = item['y_center']
                item_x = item['x_center']
                
                candidates = []
                for other in flat_items:
                    if other == item:
                        continue
                    # To the right on the same line
                    if abs(other['y_center'] - item_y) < 30 and other['x_center'] > item_x:
                        candidates.append(other)
                    # Directly below
                    elif other['y_center'] > item_y and other['y_center'] - item_y < 120:
                        candidates.append(other)
                
                if candidates:
                    # Sort candidates: prioritize same line right, then directly below
                    candidates.sort(key=lambda c: (abs(c['y_center'] - item_y), c['x_center']))
                    # Return the first viable candidate
                    for c in candidates:
                        candidate_text = c['text'].strip()
                        # Avoid matching another anchor word as the receiver
                        if len(candidate_text) > 2 and not any(fuzz.partial_ratio(a, candidate_text) > 80 for a in self.ANCHOR_KEYWORDS):
                            # Remove non-alphabet prefix like colon or dash if present
                            clean_candidate = re.sub(r'^[:\-\s]+', '', candidate_text)
                            if len(clean_candidate) > 2:
                                return clean_candidate

        # 2. If no anchor found, try finding generic merchant names or fallback
        name_prefixes = ["นาย", "นาง", "น.ส.", "MR.", "MISS", "MS.", "บจก", "บริษัท"]
        for item in flat_items:
            text = item['text'].strip()
            for prefix in name_prefixes:
                if text.startswith(prefix):
                    return text
                    
        return "Unknown Receiver"

    def process_image(self, image_path):
        try:
            logging.info(f"Extracting text from {image_path}")
            # detail=1 returns bounding boxes along with text
            result = self.reader.readtext(image_path, detail=1)
            
            logging.info(f"Raw OCR Output Blocks: {len(result)}")

            lines = self.group_lines_by_y(result)

            amounts = self.parse_amounts(lines)
            date, year = self.parse_date(lines)
            
            # If multiple amounts are found, we assume sub-payments and leave receiver blank
            if len(amounts) > 1:
                receiver = ""
            else:
                receiver = self.parse_receiver(lines)

            debug_info = {
                "raw_texts": [item[1] for item in result]
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
