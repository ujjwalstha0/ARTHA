from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db

# Initialize DB on import (or use lifespan event)
init_db()

# -------- ROUTERS --------
from routers.auth_routes import router as auth_router
from routers.kyc_routes import router as kyc_router
from routers.loan_routes import router as loan_router
from routers.transaction_routes import router as transaction_router
from routers.repayment_routes import router as repayment_router
from routers.default_routes import router as default_router
from routers.audit_routes import router as audit_router
from routers import public_ledger_routes, upload_routes

app = FastAPI(
    title="Artha P2P Lending Backend",
    description="Blockchain-backed P2P lending platform",
    version="1.0.0",
)

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5175"],  # Add frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- REGISTER ROUTERS --------

from fastapi.staticfiles import StaticFiles
import os

app.include_router(auth_router)
app.include_router(kyc_router)
app.include_router(loan_router)
app.include_router(transaction_router)
app.include_router(repayment_router)
app.include_router(default_router)
app.include_router(audit_router)
app.include_router(public_ledger_routes.router)
app.include_router(upload_routes.router)

# Serve uploads
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve generated PDFs
pdf_path = os.path.join(os.path.dirname(__file__), "generated_pdfs")
if not os.path.exists(pdf_path):
    os.makedirs(pdf_path)
app.mount("/pdfs", StaticFiles(directory=pdf_path), name="pdfs")



# -------- ROOT HEALTH CHECK --------

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Artha P2P Lending Backend"
    }
