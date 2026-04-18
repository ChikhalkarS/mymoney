"""
Analysis router: returns categorised summaries and financial advice.
"""

from __future__ import annotations

import uuid as uuid_module
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.advisor import get_advice
from app.models import (
    AnalysisResponse,
    CategorySummary,
    DailySummary,
    MonthlySummary,
    Transaction,
)

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"

router = APIRouter(prefix="/api", tags=["analysis"])


def _load_df(file_id: str) -> pd.DataFrame:
    # Parse file_id as a UUID to validate format and produce a canonical,
    # user-input-independent string – prevents path traversal.
    try:
        safe_id = str(uuid_module.UUID(file_id))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid file_id format.")
    # Build path from the canonical UUID string and confirm it stays in UPLOADS_DIR
    path = (UPLOADS_DIR / f"{safe_id}.json").resolve()
    uploads_root = UPLOADS_DIR.resolve()
    if not str(path).startswith(str(uploads_root) + "/"):
        raise HTTPException(status_code=400, detail="Invalid file_id.")
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for file_id '{safe_id}'. Upload a file first.",
        )
    df = pd.read_json(path, orient="records")
    df["date"] = pd.to_datetime(df["date"])
    return df


@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
def get_analysis(file_id: str):
    """
    Return category breakdown, monthly totals, daily cash flow, and AI advice
    for the previously uploaded file identified by *file_id*.
    """
    df = _load_df(file_id)

    # Only consider expenses (positive amounts)
    expenses = df[df["amount"] > 0].copy()

    # --- Category summary ---
    cat_totals = expenses.groupby("category")["amount"].sum()
    grand_total = cat_totals.sum() or 1  # avoid division by zero

    categories = [
        CategorySummary(
            category=cat,
            total=round(float(total), 2),
            percentage=round(float(total / grand_total) * 100, 2),
        )
        for cat, total in cat_totals.sort_values(ascending=False).items()
    ]

    # --- Monthly summary ---
    expenses["month"] = expenses["date"].dt.to_period("M").astype(str)
    monthly_group = expenses.groupby(["month", "category"])["amount"].sum()
    monthly_totals = expenses.groupby("month")["amount"].sum()

    monthly: list[MonthlySummary] = []
    for month, total in monthly_totals.sort_index().items():
        cat_breakdown = monthly_group.get(month, {})
        if hasattr(cat_breakdown, "to_dict"):
            cat_breakdown = {k: round(float(v), 2) for k, v in cat_breakdown.items()}
        else:
            cat_breakdown = {}
        monthly.append(
            MonthlySummary(
                month=str(month),
                total=round(float(total), 2),
                categories=cat_breakdown,
            )
        )

    # --- Daily summary ---
    expenses["day"] = expenses["date"].dt.strftime("%Y-%m-%d")
    daily_totals = expenses.groupby("day")["amount"].sum()
    daily = [
        DailySummary(date=day, total=round(float(total), 2))
        for day, total in daily_totals.sort_index().items()
    ]

    # --- Transactions list (all rows) ---
    transactions = [
        Transaction(
            date=row["date"].strftime("%Y-%m-%d"),
            description=str(row["description"]),
            amount=float(row["amount"]),
            category=str(row["category"]),
        )
        for _, row in df.sort_values("date").iterrows()
    ]

    # --- AI / rule-based advice ---
    cat_totals_dict = {k: float(v) for k, v in cat_totals.items()}
    advice = get_advice(cat_totals_dict)

    return AnalysisResponse(
        categories=categories,
        monthly=monthly,
        daily=daily,
        transactions=transactions,
        advice=advice,
    )
