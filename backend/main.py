"""
MyMoney FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, analysis

app = FastAPI(
    title="MyMoney API",
    description="Personal finance backend – upload bank statements and get insights.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS – allow the Next.js dev server and any local origins
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "MyMoney API is running."}
