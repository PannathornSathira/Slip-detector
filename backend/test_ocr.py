import sys
import os
import easyocr
from services.ocr_parser import SlipParser

def test():
    image_path = "/Users/bossthemeow/Desktop/Development_Projects/Side_project/slip_reading/slip_pictures/LINE_ALBUM_คชจ._251104_1.jpg"
    if not os.path.exists(image_path):
        # Let's try to list first image in that folder if this one doesn't exist
        folder = "/Users/bossthemeow/Desktop/Development_Projects/Side_project/slip_reading/slip_pictures"
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
            if files:
                image_path = os.path.join(folder, files[0])
            else:
                print("No files found in slip_pictures")
                return
        else:
            print(f"Error: Folder not found at {folder}")
            return
            
    print(f"Testing on image: {image_path}")
    
    # 1. Run raw easyocr
    reader = easyocr.Reader(['th', 'en'])
    raw_results = reader.readtext(image_path, detail=1)
    
    print("\n--- Raw EasyOCR Output (Sorted by coordinates/lines) ---")
    parser = SlipParser()
    lines = parser.group_lines_by_y(raw_results)
    for idx, line in enumerate(lines):
        items_str = " | ".join([f"[{item['text']} (x:{int(item['x_center'])}, y:{int(item['y_center'])})]" for item in line['items']])
        print(f"Line {idx+1} (y_center: {int(line['y_center'])}): {items_str}")
        
    print("\n--- Run SlipParser ---")
    records = parser.process_image(image_path)
    import pprint
    pprint.pprint(records)

if __name__ == "__main__":
    test()
