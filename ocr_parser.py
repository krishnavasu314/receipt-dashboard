import pytesseract
from PIL import Image
import re
import os
from pdf2image import convert_from_path

# Placeholder for OCR and parsing logic

def extract_fields(text: str) -> dict:
    try:
        vendor = re.search(r"Vendor[:\s]*([\w &]+)", text, re.IGNORECASE)
        date = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        amount = re.search(r"Amount[:\s]*([\d.]+)", text, re.IGNORECASE)
        category = None  # Could be mapped from vendor in future
        return {
            "vendor": vendor.group(1) if vendor else "Unknown Vendor",
            "date": date.group(1) if date else "2023-01-01",
            "amount": float(amount.group(1)) if amount else 0.0,
            "category": category
        }
    except Exception as e:
        print(f"Parsing error: {e}")
        return {
            "vendor": "Unknown Vendor",
            "date": "2023-01-01",
            "amount": 0.0,
            "category": None
        }

def parse_receipt(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
        elif ext == ".pdf":
            images = convert_from_path(file_path)
            text = " ".join([pytesseract.image_to_string(img) for img in images])
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            return {
                "vendor": "Unsupported file type",
                "date": "",
                "amount": 0.0,
                "category": None
            }
        return extract_fields(text)
    except Exception as e:
        print(f"OCR/parsing error: {e}")
        return {
            "vendor": "Unknown Vendor",
            "date": "2023-01-01",
            "amount": 0.0,
            "category": None
        }



