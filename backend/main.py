"""
MyMoney FastAPI application entry point.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, analysis

app = FastAPI(
    title="MyMoney API",
    description="Personal finance backend – upload bank statements and get insights.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS – configurable via ALLOWED_ORIGINS env var (comma-separated).
# Defaults to "*" so any frontend origin can reach the public API.
# ---------------------------------------------------------------------------
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
if _raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "MyMoney API is running."}
