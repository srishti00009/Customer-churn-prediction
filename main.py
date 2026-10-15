from __future__ import annotations

import hashlib
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import auth_db
from utils.predictor import predict_churn, get_dashboard_metrics

app = FastAPI(title="ChurnGuard AI", description="Customer Churn Prediction & Retention System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_tokens: dict[str, dict] = {}

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class PredictRequest(BaseModel):
    gender: str = ""
    senior_citizen: str = "0"
    partner: str = ""
    dependents: str = ""
    tenure: float = 12
    contract: str = ""
    internet_service: str = ""
    phone_service: str = ""
    multiple_lines: str = ""
    online_security: str = ""
    online_backup: str = ""
    device_protection: str = ""
    tech_support: str = ""
    streaming_tv: str = ""
    streaming_movies: str = ""
    monthly_charges: float = 70
    total_charges: float = 1500
    paperless_billing: str = ""
    payment_method: str = ""



@app.post("/api/auth/register")
def register(req: RegisterRequest):
    auth_db.init_db()
    success, msg = auth_db.register_user(req.username, req.email, req.password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/api/auth/login")
def login(req: LoginRequest):
    auth_db.init_db()
    success, result = auth_db.login_user(req.username, req.password)
    if not success:
        raise HTTPException(status_code=401, detail=result)
    token = hashlib.sha256(f"{result['id']}:{secrets.token_hex(16)}".encode()).hexdigest()
    _tokens[token] = dict(result)
    return {"token": token, "user": {"id": result["id"], "username": result["username"], "email": result.get("email", "")}}

def _get_user(token: str) -> dict:
    user = _tokens.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def _extract_token(authorization: str) -> str:
    if not authorization:
        return ""
    if not authorization.lower().startswith("bearer "):
        return ""
    return authorization.split(" ", 1)[1].strip()


@app.post("/api/predict")
def predict(req: PredictRequest, authorization: str = Header(default="")):
    user = _get_user(_extract_token(authorization))
    result = predict_churn(gender=req.gender, senior_citizen=req.senior_citizen, partner=req.partner, dependents=req.dependents, tenure=req.tenure, contract=req.contract, internet_service=req.internet_service, phone_service=req.phone_service, multiple_lines=req.multiple_lines, online_security=req.online_security, online_backup=req.online_backup, device_protection=req.device_protection, tech_support=req.tech_support, streaming_tv=req.streaming_tv, streaming_movies=req.streaming_movies, monthly_charges=req.monthly_charges, total_charges=req.total_charges, paperless_billing=req.paperless_billing, payment_method=req.payment_method)
    result["user_id"] = user["id"]
    return result


@app.get("/api/dashboard/metrics")
def dashboard_metrics(authorization: str = Header(default="")):
    _get_user(_extract_token(authorization))
    return get_dashboard_metrics()

app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True), name="frontend")

if __name__ == "__main__":
    auth_db.init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
