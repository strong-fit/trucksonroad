from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from database import db
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_current_user, get_jwt_secret, JWT_ALGORITHM
)
from models import LoginRequest, CustomerRegister
import jwt

router = APIRouter()


@router.post("/auth/login")
async def login(request: Request, response: Response, body: LoginRequest):
    email = body.email.lower().strip()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("count", 0) >= 5:
        last = attempt.get("last_attempt")
        if last and datetime.now(timezone.utc) - datetime.fromisoformat(str(last)) < timedelta(minutes=15):
            raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte 15 Minuten warten.")
        await db.login_attempts.delete_one({"identifier": identifier})
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
        raise HTTPException(status_code=401, detail="Ungueltige Anmeldedaten")
    await db.login_attempts.delete_one({"identifier": identifier})
    uid = str(user["_id"])
    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
    response.set_cookie(key="refresh_token", value=rt, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": uid, "email": user["email"], "name": user.get("name", ""), "role": user.get("role", "user")}


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}


@router.get("/auth/me")
async def get_me(request: Request):
    return await get_current_user(request)


@router.post("/auth/refresh")
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        at = create_access_token(str(user["_id"]), user["email"])
        response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
        return {"message": "Refreshed"}
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/auth/register")
async def register_customer(body: CustomerRegister, response: Response):
    email = body.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
    user_doc = {
        "email": email,
        "password_hash": hash_password(body.password),
        "name": f"{body.first_name} {body.last_name}",
        "first_name": body.first_name,
        "last_name": body.last_name,
        "company": body.company or "",
        "phone": body.phone or "",
        "role": "customer",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    uid = str(result.inserted_id)
    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    response.set_cookie(key="access_token", value=at, httponly=True, secure=False, samesite="lax", max_age=7200, path="/")
    response.set_cookie(key="refresh_token", value=rt, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return {"id": uid, "email": email, "name": user_doc["name"], "role": "customer"}
