from pydantic import BaseModel
from typing import Optional


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    category: Optional[str] = None
    transaction_type: Optional[str] = None


class UploadResponse(BaseModel):
    message: str
    total_rows: int
    file_id: str


class CategorySummary(BaseModel):
    category: str
    total: float
    percentage: float


class MonthlySummary(BaseModel):
    month: str
    total: float
    categories: dict


class DailySummary(BaseModel):
    date: str
    total: float


class AnalysisResponse(BaseModel):
    categories: list[CategorySummary]
    monthly: list[MonthlySummary]
    daily: list[DailySummary]
    transactions: list[Transaction]
    advice: str
