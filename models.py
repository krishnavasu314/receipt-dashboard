from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    date = Column(String, index=True)
    amount = Column(Float)
    category = Column(String, index=True)
    filename = Column(String)

class ReceiptIn(BaseModel):
    vendor: str
    date: str
    amount: float
    category: Optional[str] = None

class ReceiptOut(ReceiptIn):
    id: int
    filename: str






