from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from database import db
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_current_user, get_jwt_secret, JWT_ALGORITHM
)
from models import LoginRequest, CustomerRegister, CustomerProfileComplete
from services.email import get_email_t, send_email_background
import jwt
import uuid
import os
import random

router = APIRouter()

IS_HTTPS = os.environ.get("REACT_APP_BACKEND_URL", "").startswith("https") or os.environ.get("BACKEND_URL", "").startswith("https")


def set_auth_cookies(response: Response, access_token: str, refresh_token: str = None):
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=IS_HTTPS, samesite="lax", max_age=7200, path="/")
    if refresh_token:
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=IS_HTTPS, samesite="lax", max_age=604800, path="/")


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
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    await db.login_attempts.delete_one({"identifier": identifier})
    uid = str(user["_id"])
    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    set_auth_cookies(response, at, rt)
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
        set_auth_cookies(response, at)
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
    set_auth_cookies(response, at, rt)
    return {"id": uid, "email": email, "name": user_doc["name"], "role": "customer"}


# --- PASSWORDLESS AUTH (E-Mail + Code) ---

def build_verification_code_email(code: str, lang: str = "de") -> str:
    labels = {
        "de": {"title": "Ihr Bestätigungscode", "text": "Verwenden Sie den folgenden Code, um sich bei TrucksOnRoad anzumelden:", "expire": "Dieser Code ist 10 Minuten gültig.", "ignore": "Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail."},
        "en": {"title": "Your Verification Code", "text": "Use the following code to sign in to TrucksOnRoad:", "expire": "This code is valid for 10 minutes.", "ignore": "If you did not request this, please ignore this email."},
        "fr": {"title": "Votre code de vérification", "text": "Utilisez le code suivant pour vous connecter à TrucksOnRoad :", "expire": "Ce code est valide pendant 10 minutes.", "ignore": "Si vous n'avez pas fait cette demande, ignorez cet e-mail."},
        "it": {"title": "Il tuo codice di verifica", "text": "Usa il seguente codice per accedere a TrucksOnRoad:", "expire": "Questo codice è valido per 10 minuti.", "ignore": "Se non hai effettuato questa richiesta, ignora questa e-mail."},
    }
    l = labels.get(lang, labels["de"])
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;text-align:center;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">{l['title']}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{l['text']}</p>
        <div style="margin:1.5rem 0;padding:1.2rem;background:#fff;border:2px solid #4db6ac;border-radius:12px;display:inline-block;">
          <span style="font-family:'Bebas Neue',monospace;font-size:2.5rem;letter-spacing:0.3em;color:#1a1a18;font-weight:700;">{code}</span>
        </div>
        <p style="color:#9c9c94;font-size:0.8rem;margin-top:1rem;">{l['expire']}</p>
        <p style="color:#9c9c94;font-size:0.8rem;">{l['ignore']}</p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


@router.post("/auth/send-code")
async def send_verification_code(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Gültige E-Mail-Adresse erforderlich")

    # Rate limit: max 3 codes per email per 10 minutes
    ten_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    recent_count = await db.verification_codes.count_documents({
        "email": email, "created_at": {"$gte": ten_min_ago}
    })
    if recent_count >= 3:
        raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte warten Sie 10 Minuten.")

    # Block admin emails from passwordless login
    admin_user = await db.users.find_one({"email": email, "role": "admin"})
    if admin_user:
        raise HTTPException(status_code=400, detail="Admin-Konten verwenden bitte den Admin-Login.")

    code = f"{random.randint(0, 999999):06d}"
    await db.verification_codes.insert_one({
        "email": email,
        "code": code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
        "used": False,
        "attempts": 0
    })
    lang = body.get("lang", "de")
    subject_map = {"de": "Ihr Bestätigungscode", "en": "Your Verification Code", "fr": "Votre code de vérification", "it": "Il tuo codice di verifica"}
    html = build_verification_code_email(code, lang)
    background_tasks.add_task(send_email_background, email, f"{subject_map.get(lang, subject_map['de'])} – TrucksOnRoad", html)
    return {"message": "Code gesendet", "email": email}


@router.post("/auth/verify-code")
async def verify_code(request: Request, response: Response):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    code = body.get("code", "").strip()
    if not email or not code:
        raise HTTPException(status_code=400, detail="E-Mail und Code erforderlich")

    # Find the latest unused code for this email
    code_doc = await db.verification_codes.find_one(
        {"email": email, "used": False},
        sort=[("created_at", -1)]
    )
    if not code_doc:
        raise HTTPException(status_code=400, detail="Kein gültiger Code gefunden. Bitte neuen Code anfordern.")

    # Check if expired
    expires = datetime.fromisoformat(code_doc["expires_at"])
    if datetime.now(timezone.utc) > expires:
        await db.verification_codes.update_one({"_id": code_doc["_id"]}, {"$set": {"used": True}})
        raise HTTPException(status_code=400, detail="Code abgelaufen. Bitte neuen Code anfordern.")

    # Max 5 wrong attempts per code
    if code_doc.get("attempts", 0) >= 5:
        await db.verification_codes.update_one({"_id": code_doc["_id"]}, {"$set": {"used": True}})
        raise HTTPException(status_code=400, detail="Zu viele Fehlversuche. Bitte neuen Code anfordern.")

    if code_doc["code"] != code:
        await db.verification_codes.update_one({"_id": code_doc["_id"]}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail="Falscher Code")

    # Mark code as used
    await db.verification_codes.update_one({"_id": code_doc["_id"]}, {"$set": {"used": True}})
    # Invalidate all other codes for this email
    await db.verification_codes.update_many({"email": email, "used": False}, {"$set": {"used": True}})

    # Find or create user
    user = await db.users.find_one({"email": email})
    is_new = False
    if not user:
        # Create new user with minimal info
        user_doc = {
            "email": email,
            "password_hash": "",
            "name": "",
            "first_name": "",
            "last_name": "",
            "company": "",
            "phone": "",
            "mobile": "",
            "street": "",
            "plz": "",
            "city": "",
            "role": "customer",
            "profile_complete": False,
            "email_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.users.insert_one(user_doc)
        uid = str(result.inserted_id)
        is_new = True
    else:
        uid = str(user["_id"])
        is_new = not user.get("profile_complete", False) and not user.get("first_name")
        # Mark email as verified
        await db.users.update_one({"_id": user["_id"]}, {"$set": {"email_verified": True}})

    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)
    set_auth_cookies(response, at, rt)
    return {
        "id": uid, "email": email, "role": "customer",
        "is_new": is_new, "profile_complete": not is_new
    }


@router.post("/auth/complete-profile")
async def complete_profile(request: Request, body: CustomerProfileComplete):
    user = await get_current_user(request)
    name = f"{body.first_name} {body.last_name}".strip()
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {
            "first_name": body.first_name,
            "last_name": body.last_name,
            "street": body.street,
            "plz": body.plz,
            "city": body.city,
            "mobile": body.mobile,
            "phone": body.mobile,
            "company": body.company or "",
            "name": name,
            "profile_complete": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    return {"message": "Profil vervollständigt", "name": name}


def build_reset_email(reset_url: str, name: str, lang: str = "de") -> str:
    t = get_email_t(lang)
    labels = {
        "de": {"title": "Passwort zurücksetzen", "text": "Sie haben eine Passwortzurücksetzung angefordert. Klicken Sie auf den Button, um ein neues Passwort zu setzen:", "btn": "Neues Passwort setzen", "expire": "Dieser Link ist 1 Stunde gültig.", "ignore": "Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail."},
        "en": {"title": "Reset Password", "text": "You have requested a password reset. Click the button below to set a new password:", "btn": "Set New Password", "expire": "This link is valid for 1 hour.", "ignore": "If you did not request this, please ignore this email."},
        "fr": {"title": "Réinitialiser le mot de passe", "text": "Vous avez demandé une réinitialisation de mot de passe. Cliquez sur le bouton pour définir un nouveau mot de passe :", "btn": "Définir un nouveau mot de passe", "expire": "Ce lien est valide pendant 1 heure.", "ignore": "Si vous n'avez pas fait cette demande, ignorez cet e-mail."},
        "it": {"title": "Reimposta password", "text": "Hai richiesto la reimpostazione della password. Clicca sul pulsante per impostare una nuova password:", "btn": "Imposta nuova password", "expire": "Questo link è valido per 1 ora.", "ignore": "Se non hai effettuato questa richiesta, ignora questa e-mail."},
    }
    l = labels.get(lang, labels["de"])
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{l['title']}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{t['hello'].format(name=name)}</p>
        <p style="color:#6b6b64;line-height:1.6;">{l['text']}</p>
        <div style="text-align:center;margin:2rem 0;">
          <a href="{reset_url}" style="background:#4db6ac;color:#fff;padding:0.75rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;">{l['btn']}</a>
        </div>
        <p style="color:#9c9c94;font-size:0.8rem;">{l['expire']}</p>
        <p style="color:#9c9c94;font-size:0.8rem;">{l['ignore']}</p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


@router.post("/auth/forgot-password")
async def forgot_password(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="E-Mail fehlt")
    user = await db.users.find_one({"email": email})
    if not user:
        return {"message": "OK"}
    token = str(uuid.uuid4())
    await db.password_resets.delete_many({"email": email})
    await db.password_resets.insert_one({
        "email": email,
        "token": token,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "used": False
    })
    frontend_url = request.headers.get("origin", "https://trucksonroad.ch")
    role = user.get("role", "customer")
    reset_path = "/admin/passwort-reset" if role == "admin" else "/konto/passwort-reset"
    reset_url = f"{frontend_url}{reset_path}?token={token}"
    lang = user.get("lang", "de")
    name = user.get("name", email.split("@")[0])
    subject_map = {"de": "Passwort zurücksetzen", "en": "Reset Password", "fr": "Réinitialiser le mot de passe", "it": "Reimposta password"}
    html = build_reset_email(reset_url, name, lang)
    background_tasks.add_task(send_email_background, email, f"{subject_map.get(lang, subject_map['de'])} – TrucksOnRoad", html)
    return {"message": "OK"}


@router.post("/auth/reset-password")
async def reset_password(request: Request):
    body = await request.json()
    token = body.get("token", "")
    new_password = body.get("password", "")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token und Passwort erforderlich")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 6 Zeichen haben")
    reset_doc = await db.password_resets.find_one({"token": token, "used": False})
    if not reset_doc:
        raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Link")
    expires = datetime.fromisoformat(reset_doc["expires_at"])
    if datetime.now(timezone.utc) > expires:
        await db.password_resets.update_one({"token": token}, {"$set": {"used": True}})
        raise HTTPException(status_code=400, detail="Link abgelaufen")
    result = await db.users.update_one(
        {"email": reset_doc["email"]},
        {"$set": {"password_hash": hash_password(new_password)}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Benutzer nicht gefunden")
    await db.password_resets.update_one({"token": token}, {"$set": {"used": True}})
    return {"message": "Passwort erfolgreich geändert"}


@router.put("/auth/change-password")
async def change_password(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Altes und neues Passwort erforderlich")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 6 Zeichen haben")
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    if not user_doc or not verify_password(old_password, user_doc["password_hash"]):
        raise HTTPException(status_code=400, detail="Altes Passwort ist falsch")
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"password_hash": hash_password(new_password)}}
    )
    return {"message": "Passwort erfolgreich geändert"}
