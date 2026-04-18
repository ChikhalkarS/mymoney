"""
Upload router: accepts CSV or Excel files and returns a processed file_id.
"""

from __future__ import annotations

import io
import json
import os
import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.categorizer import categorize_transaction
from app.models import UploadResponse

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api", tags=["upload"])

REQUIRED_COLUMNS_ALIASES = {
    "date": ["date", "transaction date", "trans date", "posting date", "value date"],
    "description": ["description", "merchant", "details", "narration", "memo",
                    "transaction description", "particulars"],
    "amount": ["amount", "debit", "credit", "transaction amount", "value"],
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw columns to canonical names (date, description, amount)."""
    col_map: dict[str, str] = {}
    lower_cols = {c.lower().strip(): c for c in df.columns}

    for canonical, aliases in REQUIRED_COLUMNS_ALIASES.items():
        for alias in aliases:
            if alias in lower_cols:
                col_map[lower_cols[alias]] = canonical
                break

    df = df.rename(columns=col_map)

    missing = [c for c in ("date", "description", "amount") if c not in df.columns]
    if missing:
        raise ValueError(
            f"Could not find required columns: {missing}. "
            "Expected columns named (case-insensitive): date, description, amount."
        )
    return df


def _parse_upload(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content))
    else:
        # Try CSV first, then Excel
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception:
            df = pd.read_excel(io.BytesIO(content))

    return df


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Accept a CSV or Excel bank statement, clean it, categorize transactions,
    and persist the result as JSON for later analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    try:
        df = _parse_upload(file)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    try:
        df = _normalise_columns(df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # --- Clean data ---
    df = df[["date", "description", "amount"]].copy()
    df["description"] = df["description"].fillna("").astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # --- Categorize ---
    df["category"] = df.apply(
        lambda row: categorize_transaction(row["description"], row["amount"]),
        axis=1,
    )

    # --- Persist ---
    file_id = str(uuid.uuid4())
    out_path = UPLOADS_DIR / f"{file_id}.json"
    df.to_json(out_path, orient="records", date_format="iso")

    return UploadResponse(
        message="File processed successfully.",
        total_rows=len(df),
        file_id=file_id,
    )
