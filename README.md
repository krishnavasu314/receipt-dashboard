# Receipt/Bill Uploader & Analyzer

## Overview
A full-stack mini-application for uploading receipts and bills (e.g., electricity, internet, groceries). The app extracts structured data using OCR and rule-based logic, then presents summarized insights such as total spend, top vendors, and billing trends. It demonstrates core algorithms (search, sort, aggregation) with a clean backend and an interactive dashboard UI.

---

## Features
- Upload receipts/bills in `.jpg`, `.png`, `.pdf`, or `.txt` formats
- Automatic extraction of vendor, date, amount, and category
- Data stored in normalized SQLite database
- Keyword and range search (date, amount)
- Sort by amount, date, or vendor
- Aggregation: sum, mean, median, mode, vendor frequency
- Time-series spend trend (monthly line chart)
- Manual correction of parsed fields in the UI
- Export table as CSV or JSON
- User-friendly error handling and validation

---

## Setup Instructions

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
- The backend will run at http://127.0.0.1:8000

### 2. Frontend (Streamlit Dashboard)
Open a new terminal, activate the virtual environment, and run:
```bash
cd backend
venv\Scripts\activate
streamlit run app.py
```
- The dashboard will open at http://localhost:8501

---

## Usage
1. **Upload a receipt/bill** (image, PDF, or text file) in the dashboard.
2. **View all receipts** in a searchable, sortable table.
3. **Edit/correct** any parsed field by expanding the row and saving changes.
4. **Filter by date or amount** using the range filters above the table.
5. **Export** the table as CSV or JSON.
6. **See statistics** (total, mean, median, mode, vendor frequency) and a monthly spend trend chart.

---

## Design Choices & Architecture
- **Backend:** FastAPI for API, SQLAlchemy for SQLite ORM, Pydantic for validation, Tesseract OCR for image/PDF parsing.
- **Frontend:** Streamlit for rapid, interactive dashboards.
- **Algorithms:** Linear search, custom quicksort, Python statistics for aggregation, Counter for frequency, pandas for time-series.
- **Manual correction:** Users can edit any parsed field for real-world flexibility.
- **Export:** CSV/JSON export for reporting and backup.

---

## Limitations & Assumptions
- Parsing is rule-based and may not extract all fields from highly unstructured or foreign-language receipts.
- Only basic currency and date formats are supported.
- No authentication or user management (single-user demo app).
- Multi-currency and multi-language support are not implemented.


---

## How to Test
- Try uploading different file types (image, PDF, text).
- Use the edit feature to correct any parsing errors.
- Use the filters and export features.
- Check the statistics and charts update as you add/edit data.

---

## Author & Acknowledgments
- Developed as a Python intern assignment.
- Uses open-source libraries: FastAPI, Streamlit, SQLAlchemy, pytesseract, pandas, etc. 
