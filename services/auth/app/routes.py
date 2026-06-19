import json
import os

import redis
from fastapi import APIRouter, Header, HTTPException

from app.auth import create_token, decode_token, hash_password, verify_password
from app.models import TokenResponse, UserLogin, UserRegister

router = APIRouter()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


@router.post("/register/", status_code=201)
def register(user: UserRegister):
    if redis_client.exists(f"user:{user.username}"):
        raise HTTPException(status_code=409, detail="Username already exists")

    user_data = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
    }
    redis_client.set(f"user:{user.username}", json.dumps(user_data))
    return {"message": "User registered successfully", "username": user.username}


@router.post("/login/", response_model=TokenResponse)
def login(credentials: UserLogin):
    user_json = redis_client.get(f"user:{credentials.username}")
    if not user_json:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = json.loads(user_json)
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": credentials.username, "email": user["email"]})
    return TokenResponse(access_token=token)


@router.get("/verify/")
def verify(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "").replace("bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"valid": True, "username": payload["sub"], "email": payload.get("email")}
