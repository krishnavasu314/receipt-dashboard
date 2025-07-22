from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
from ocr_parser import parse_receipt
from db import SessionLocal
from models import Receipt
from algorithms import linear_search, quicksort, aggregate_sum
from statistics import mean, median, mode, StatisticsError
from collections import Counter

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ReceiptIn(BaseModel):
    vendor: str
    date: str
    amount: float
    category: str = None

class ReceiptUpdate(BaseModel):
    vendor: str
    date: str
    amount: float
    category: str = None

@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    db = SessionLocal()
    try:
        # Check for duplicate filename
        existing_file = db.query(Receipt).filter(Receipt.filename == file.filename).first()
        if existing_file:
            raise HTTPException(status_code=400, detail="A file with this name has already been uploaded.")
        # Save file
        with open(file_location, "wb") as f:
            f.write(await file.read())
        # Parse and check for duplicate data
        parsed = parse_receipt(file_location)
        existing_data = db.query(Receipt).filter(
            Receipt.vendor == parsed["vendor"],
            Receipt.date == parsed["date"],
            Receipt.amount == parsed["amount"]
        ).first()
        if existing_data:
            raise HTTPException(status_code=400, detail="A receipt with these details already exists.")
        # Store receipt
        receipt = Receipt(
            vendor=parsed["vendor"],
            date=parsed["date"],
            amount=parsed["amount"],
            category=parsed["category"],
            filename=file.filename
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return {"filename": file.filename, "status": "uploaded", "parsed": parsed}
    finally:
        db.close()

@app.get("/receipts")
def list_receipts():
    db = SessionLocal()
    try:
        receipts = db.query(Receipt).all()
        return [
            {
                "id": r.id,
                "vendor": r.vendor,
                "date": r.date,
                "amount": r.amount,
                "category": r.category,
                "filename": r.filename
            }
            for r in receipts
        ]
    finally:
        db.close()

@app.get("/search")
def search_receipts(q: str):
    db = SessionLocal()
    try:
        receipts = db.query(Receipt).all()
        results = linear_search(receipts, q)
        return [
            {
                "id": r.id,
                "vendor": r.vendor,
                "date": r.date,
                "amount": r.amount,
                "category": r.category,
                "filename": r.filename
            }
            for r in results
        ]
    finally:
        db.close()

@app.get("/sort")
def sort_receipts(field: str = "amount", order: str = "desc"):
    db = SessionLocal()
    try:
        receipts = db.query(Receipt).all()
        key_func = lambda r: getattr(r, field, None)
        sorted_receipts = quicksort(receipts, key_func)
        if order == "desc":
            sorted_receipts = list(reversed(sorted_receipts))
        return [
            {
                "id": r.id,
                "vendor": r.vendor,
                "date": r.date,
                "amount": r.amount,
                "category": r.category,
                "filename": r.filename
            }
            for r in sorted_receipts
        ]
    finally:
        db.close()

@app.get("/stats")
def stats():
    db = SessionLocal()
    try:
        receipts = db.query(Receipt).all()
        amounts = [r.amount for r in receipts]
        vendors = [r.vendor for r in receipts]
        total = sum(amounts)
        avg = mean(amounts) if amounts else 0.0
        med = median(amounts) if amounts else 0.0
        try:
            mod = mode(amounts) if amounts else 0.0
        except StatisticsError:
            mod = None
        # Vendor frequency
        vendor_freq = Counter(vendors)
        return {
            "total": total,
            "mean": avg,
            "median": med,
            "mode": mod,
            "vendor_frequency": vendor_freq
        }
    finally:
        db.close()

@app.patch("/update/{receipt_id}")
def update_receipt(receipt_id: int, update: ReceiptUpdate = Body(...)):
    db = SessionLocal()
    try:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        receipt.vendor = update.vendor
        receipt.date = update.date
        receipt.amount = update.amount
        receipt.category = update.category
        db.commit()
        db.refresh(receipt)
        return {
            "id": receipt.id,
            "vendor": receipt.vendor,
            "date": receipt.date,
            "amount": receipt.amount,
            "category": receipt.category,
            "filename": receipt.filename
        }
    finally:
        db.close()



