"""
Backend (FastAPI) - Generic Proxy Server עבור פרויקט Zovex
===========================================================
קובץ: main.py

התקנה:
    pip install fastapi uvicorn httpx

הרצה:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import httpx
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────────────────────
#  !! הכנס כאן את הדומיין שלך !!
#  דוגמאות:
#    "https://zovex.co.il"
#    "https://davidggjg.github.io"
# ─────────────────────────────────────────────────────────────
ALLOWED_ORIGIN = "https://davidggjg.github.io"

# ─────────────────────────────────────────────────────────────
#  רשימת דומיינים מותרים לבקשות (הגנת SSRF)
#  הוסף כאן רק דומיינים שהשרת מורשה לפנות אליהם
# ─────────────────────────────────────────────────────────────
ALLOWED_TARGETS = [
    "www.mako.co.il",
    "mako.co.il",
    "d2249b6f08tjt0.cloudfront.net",
]

app = FastAPI(title="Zovex Generic Proxy", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── headers קבועים לכל הבקשות למאקו ────────────────────────
MAKO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 16; Mobile; rv:144.0) Gecko/144.0 Firefox/144.0",
    "Referer": "https://www.mako.co.il/",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
}


def validate_target(url: str) -> str:
    """בודקת שה-URL מותר ומחזירה אותו, זורקת 403 אחרת."""
    if not url:
        raise HTTPException(status_code=400, detail="url is required")
    try:
        domain = urlparse(url).netloc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    if domain not in ALLOWED_TARGETS:
        raise HTTPException(
            status_code=403,
            detail=f"Target domain '{domain}' is not allowed",
        )
    return url


# ─── Endpoint: פרוקסי גנרי ───────────────────────────────────
@app.post("/api/proxy")
async def proxy_request(request: Request):
    """
    מקבל מה-Frontend:
    {
        "url":     "https://www.mako.co.il/...",   // ה-URL לשליחת הבקשה
        "payload": { ... }                          // ה-Payload שנלכד מ-DevTools
    }

    שולח POST למאקו עם ה-Payload ומחזיר את התגובה כמו שהיא.
    """
    data = await request.json()
    target_url = validate_target(data.get("url", ""))
    payload = data.get("payload", {})

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            resp = await client.post(target_url, data=payload, headers=MAKO_HEADERS)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Cannot reach target: {str(e)}")

        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="Mako returned 403 — Payload or token may be expired")
        if not resp.is_success:
            raise HTTPException(status_code=502, detail=f"Mako returned {resp.status_code}")

        try:
            return resp.json()
        except Exception:
            # אם התגובה לא JSON, מחזירים כטקסט
            return {"raw": resp.text}


# ─── Endpoint: משיכת קישור Stream (GET) ──────────────────────
@app.get("/api/stream")
async def get_stream(url: str):
    """
    מקבל קישור m3u8 ובודק שהוא נגיש.
    משמש ל-on-demand refresh מה-Frontend.

    שימוש: GET /api/stream?url=https://d2249b6f08tjt0.cloudfront.net/...
    """
    validate_target(url)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Cannot reach stream: {str(e)}")

        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail="Stream token expired")
        if not resp.is_success:
            raise HTTPException(status_code=502, detail=f"Stream returned {resp.status_code}")

        return {"url": str(resp.url), "status": "ok"}


# ─── Endpoint: בדיקת תקינות ──────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "allowed_origin": ALLOWED_ORIGIN}
