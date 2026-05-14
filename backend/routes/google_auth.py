"""
Google OAuth login for customers — using own Google Cloud project credentials.

REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
Redirect-URI is built dynamically from the incoming request URL.

Flow:
  1) GET /api/auth/google/login    → 302 → Google consent
  2) Google → 302 → /api/auth/google/callback?code=...&state=...
  3) Backend exchanges code → user info → finds/creates user → sets JWT cookie → 302 → /konto
"""
import os
import secrets
import logging
import urllib.parse
from typing import Optional
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse

from database import db
from auth import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)
router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

STATE_COOKIE = "google_oauth_state"
NEXT_COOKIE = "google_oauth_next"
STATE_MAX_AGE = 600  # 10 minutes


def _get_credentials() -> tuple[str, str]:
    cid = os.environ.get("GOOGLE_CLIENT_ID")
    secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not cid or not secret:
        raise HTTPException(status_code=500, detail="Google OAuth ist nicht konfiguriert")
    return cid, secret


def _is_https(request: Request) -> bool:
    """Trust X-Forwarded-Proto for ingress/proxy setups, fall back to request.url.scheme."""
    fwd = request.headers.get("x-forwarded-proto", "").lower()
    if fwd:
        return fwd == "https"
    return request.url.scheme == "https"


def _build_redirect_uri(request: Request) -> str:
    """
    Builds the absolute redirect URI based on the incoming request.
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    # Prefer X-Forwarded-Host (ingress) over Host header
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    scheme = "https" if _is_https(request) else "http"
    return f"{scheme}://{host}/api/auth/google/callback"


def _frontend_base(request: Request) -> str:
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    scheme = "https" if _is_https(request) else "http"
    return f"{scheme}://{host}"


def _set_auth_cookies(response: Response, request: Request, access_token: str, refresh_token: str):
    secure = _is_https(request)
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=secure,
        samesite="lax", max_age=7200, path="/",
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=secure,
        samesite="lax", max_age=604800, path="/",
    )


@router.get("/auth/google/login")
async def google_login(request: Request, next: Optional[str] = "/konto"):
    """Step 1: Build Google consent URL and redirect."""
    client_id, _ = _get_credentials()
    redirect_uri = _build_redirect_uri(request)
    state = secrets.token_urlsafe(32)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "access_type": "online",
        "include_granted_scopes": "true",
        "state": state,
        "prompt": "select_account",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    response = RedirectResponse(url=auth_url, status_code=302)
    secure = _is_https(request)
    # Short-lived state cookie for CSRF protection
    response.set_cookie(
        key=STATE_COOKIE, value=state, httponly=True, secure=secure,
        samesite="lax", max_age=STATE_MAX_AGE, path="/",
    )
    # Remember where to redirect after success (only allow internal paths)
    safe_next = next if (next and next.startswith("/") and not next.startswith("//")) else "/konto"
    response.set_cookie(
        key=NEXT_COOKIE, value=safe_next, httponly=True, secure=secure,
        samesite="lax", max_age=STATE_MAX_AGE, path="/",
    )
    return response


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    """Step 2: Validate state, exchange code for token, fetch user, create/login user, set cookies."""
    client_id, client_secret = _get_credentials()
    redirect_uri = _build_redirect_uri(request)

    qs = request.query_params
    error = qs.get("error")
    if error:
        return RedirectResponse(
            url=f"{_frontend_base(request)}/konto/login?error={urllib.parse.quote(error)}",
            status_code=302,
        )

    code = qs.get("code")
    state = qs.get("state")
    cookie_state = request.cookies.get(STATE_COOKIE)
    if not code or not state or not cookie_state or state != cookie_state:
        return RedirectResponse(
            url=f"{_frontend_base(request)}/konto/login?error=state_mismatch",
            status_code=302,
        )

    # Exchange code → tokens
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            token_resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
        except httpx.HTTPError as exc:
            logger.error(f"Google token exchange failed: {exc}")
            return RedirectResponse(
                url=f"{_frontend_base(request)}/konto/login?error=token_exchange_failed",
                status_code=302,
            )

        access_token = token_data.get("access_token")
        if not access_token:
            return RedirectResponse(
                url=f"{_frontend_base(request)}/konto/login?error=no_access_token",
                status_code=302,
            )

        try:
            user_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_resp.raise_for_status()
            profile = user_resp.json()
        except httpx.HTTPError as exc:
            logger.error(f"Google userinfo fetch failed: {exc}")
            return RedirectResponse(
                url=f"{_frontend_base(request)}/konto/login?error=userinfo_failed",
                status_code=302,
            )

    email = (profile.get("email") or "").lower().strip()
    if not email:
        return RedirectResponse(
            url=f"{_frontend_base(request)}/konto/login?error=no_email",
            status_code=302,
        )
    if not profile.get("email_verified", False):
        return RedirectResponse(
            url=f"{_frontend_base(request)}/konto/login?error=email_not_verified",
            status_code=302,
        )

    google_sub = profile.get("sub")
    given_name = profile.get("given_name", "") or ""
    family_name = profile.get("family_name", "") or ""
    full_name = profile.get("name", "") or f"{given_name} {family_name}".strip()

    # Find or create user
    user = await db.users.find_one({"email": email})
    is_new = False
    if not user:
        user_doc = {
            "email": email,
            "password_hash": "",
            "name": full_name,
            "first_name": given_name,
            "last_name": family_name,
            "company": "",
            "phone": "",
            "mobile": "",
            "street": "",
            "plz": "",
            "city": "",
            "role": "customer",
            "profile_complete": False,
            "email_verified": True,
            "auth_provider": "google",
            "google_sub": google_sub,
            "google_picture": profile.get("picture", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = await db.users.insert_one(user_doc)
        uid = str(result.inserted_id)
        is_new = True
    else:
        uid = str(user["_id"])
        # Backfill google fields, ensure verified flag
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "email_verified": True,
                "auth_provider": user.get("auth_provider") or "google",
                "google_sub": user.get("google_sub") or google_sub,
                "google_picture": user.get("google_picture") or profile.get("picture", ""),
            }},
        )
        is_new = not user.get("profile_complete", False) and not user.get("first_name")

    at = create_access_token(uid, email)
    rt = create_refresh_token(uid)

    # Redirect to next path (or /konto)
    next_path = request.cookies.get(NEXT_COOKIE) or "/konto"
    if is_new:
        next_path = "/konto/profil-vervollstaendigen"
    target = f"{_frontend_base(request)}{next_path}"

    response = RedirectResponse(url=target, status_code=302)
    _set_auth_cookies(response, request, at, rt)
    # Clear short-lived state cookies
    response.delete_cookie(STATE_COOKIE, path="/")
    response.delete_cookie(NEXT_COOKIE, path="/")
    return response
