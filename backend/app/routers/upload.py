"""
Upload router: accepts CSV, Excel, or PDF files and returns a processed file_id.
"""

from __future__ import annotations

import io
import re
import uuid
from pathlib import Path

import pandas as pd
import pdfplumber
from fastapi import APIRouter, HTTPException, UploadFile, File

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


def _parse_pdf(content: bytes) -> pd.DataFrame:
    """
    Extract transactions from a PDF bank statement.

    Strategy:
    1. Collect all tables across all pages.
    2. Pick the largest table that looks like a transaction list
       (i.e. has at least one column aliased to date/description/amount).
    3. Fall back to a line-by-line text heuristic if no suitable table is found.
    """
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        # --- Attempt table extraction ---
        all_tables: list[list[list[str | None]]] = []
        for page in pdf.pages:
            for table in page.extract_tables():
                if table and len(table) > 1:
                    all_tables.append(table)

        if all_tables:
            # Sort by row count descending; try each until one normalises OK
            all_tables.sort(key=len, reverse=True)
            for raw_table in all_tables:
                headers = [str(c).strip() if c is not None else "" for c in raw_table[0]]
                rows = [
                    [str(cell).strip() if cell is not None else "" for cell in row]
                    for row in raw_table[1:]
                    if any(cell is not None for cell in row)
                ]
                if not rows:
                    continue
                df = pd.DataFrame(rows, columns=headers)
                try:
                    return _normalise_columns(df)
                except ValueError:
                    continue  # Try the next table

        # --- Text-based fallback ---
        # Heuristic: look for lines that start with a date-like token,
        # then capture description and a numeric amount at the end.
        date_re = re.compile(
            r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})"
        )
        amount_re = re.compile(r"([\-\+]?\$?[\d,]+\.\d{2})\s*$")

        records: list[dict[str, str]] = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                date_m = date_re.match(line)
                amount_m = amount_re.search(line)
                if date_m and amount_m and date_m.end() < amount_m.start():
                    date_str = date_m.group(1)
                    amount_str = amount_m.group(1).replace("$", "").replace(",", "")
                    description = line[date_m.end(): amount_m.start()].strip()
                    records.append(
                        {"date": date_str, "description": description or "—", "amount": amount_str}
                    )

        if not records:
            raise ValueError(
                "Could not extract any transaction table from the PDF. "
                "Please ensure the PDF contains a tabular bank statement."
            )

        return pd.DataFrame(records)


def _parse_upload(file: UploadFile) -> pd.DataFrame:
    """Parse the uploaded file and return a DataFrame with canonical columns."""
    content = file.file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        # _parse_pdf already normalises columns
        return _parse_pdf(content)
    elif filename.endswith(".csv"):
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


def _is_pdf(file: UploadFile) -> bool:
    return (file.filename or "").lower().endswith(".pdf")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Accept a CSV, Excel, or PDF bank statement, clean it, categorize transactions,
    and persist the result as JSON for later analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    is_pdf = _is_pdf(file)

    try:
        df = _parse_upload(file)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    # PDF path: columns are already normalised inside _parse_pdf
    if not is_pdf:
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
