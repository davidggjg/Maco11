import httpx
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Maco Stream Proxy")

# 1. הגדרת ה-Origin שלך (שנה לכתובת האתר האמיתית שלך)
ALLOWED_ORIGIN = "https://your-username.github.io" 

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ניהול סשן גלובלי
session_cache = {"client": None, "expires_at": 0}

async def get_valid_client():
    # בדיקת תוקף סשן (שעה אחת = 3600 שניות)
    if session_cache["client"] and time.time() < session_cache["expires_at"]:
        return session_cache["client"]
    
    # יצירת סשן חדש
    client = httpx.AsyncClient(follow_redirects=True)
    
    # ה-Payload שהעתקנו מה-Network
    payload = {
        "cid": "cj2l",
        "uzl": "T6MEtpzY7tq9YQZncEHIpZmZCux9efajlzTdUcHjiyg=",
        "et": "85",
        "url": "https://www.mako.co.il/click/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm",
        "JSinfo": '{"j301":{"k1":169,"k2":188,"k3":"playIcon","k4":0,"k5":0,"k6":0,"k7":0},"j289":"7705c65e-d6ba-4e7f-bbe4-9f8757a66b80","j290":"MTlmYTQ4Y2UtY2oyai00MDBiLWFjNzAtYTdjMjg0NTIzMDZkJDE4OC42NC4yMDcuMTA1"}',
        "js_zpsbd3": "https://www.google.com/",
        "jsbd2": "96cc65e7-cj2l-e436-16a5-10a7377c643d",
        "__uzmf": "7f90007705c65e-d6ba-4e7f-bbe4-9f8757a66b801-17838497515910-0048ca02e3f764010bb10",
        "uzmx": "7f90006125d0ad-52ea-4358-b777-160c7889afec1-17838497515910-4c74e1c3a23da1ff10",
        "__uzmaj": "7705c65e-d6ba-4e7f-bbe4-9f8757a66b80",
        "__uzmbj": "1782856303",
        "__uzmcj": "931741050159",
        "__uzmdj": "1783843579",
        "__uzmlj": "T6MEtpzY7tq9YQZncEHIpZmZCux9efajlzTdUcHjiyg=",
        "__uzmfj": "7f90007705c65e-d6ba-4e7f-bbe4-9f8757a66b803-1782856303547993503391-004809e9f256d98d9d010",
        "dync": "uzmx",
        "uzmxj": "7f90006125d0ad-52ea-4358-b777-160c7889afec3-1782856303547993503391-fdeb56834c4c0f4131"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }

    # "לחיצת היד"
    await client.post("https://www.mako.co.il/c99a4269-161c-4242-a3f0-28d44fa6ce24", data=payload, headers=headers)
    
    session_cache["client"] = client
    session_cache["expires_at"] = time.time() + 3600
    return client

@app.get("/api/refresh-stream")
async def refresh_stream():
    try:
        client = await get_valid_client()
        # הכתובת של הסטרים
        stream_url = "https://d2249b6f08tjt0.cloudfront.net/k12dvr/master.m3u8"
        resp = await client.get(stream_url)
        
        if resp.status_code == 200:
            return {"url": str(resp.url)}
        else:
            # אם נכשל, ננקה את הסשן כדי שינסה שוב מאפס בבקשה הבאה
            session_cache["expires_at"] = 0
            raise HTTPException(status_code=500, detail="Failed to fetch stream")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
