import httpx
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Maco Stream Proxy")

# --- הגדרות ---
# כאן תכניס את כתובת האתר שלך ב-GitHub Pages (למשל: https://yourname.github.io)
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
    # בדיקת תוקף סשן (3600 שניות = שעה)
    if session_cache["client"] and time.time() < session_cache["expires_at"]:
        return session_cache["client"]
    
    # יצירת סשן חדש עם עוגיות (Cookies) שמחזיק את המצב
    client = httpx.AsyncClient(follow_redirects=True)
    
    # ה-Payload המעודכן שסיפקת
    payload = {
        "cid": "cj2l",
        "uzl": "T6MEtpzY7tq9YQZncEHIpZmZCux9efajlzTdUcHjiyg=",
        "et": "85",
        "url": "https://www.mako.co.il/click/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm",
        "JSinfo": '{"j301":{"k1":202,"k2":194,"k3":"playIcon","k4":0,"k5":0,"k6":0,"k7":0},"j289":"a385f5b1-4246-4c26-9f89-17e1fee3810c","j290":"Zjc4N2IyMzktY2oyai00YWNmLWIwNjAtNjdhOTkxZjA1MDM0JDE0Ny4yMzYuMjMxLjE4Mg=="}',
        "js_zpsbd3": "https://www.google.com/",
        "jsbd2": "14c262c5-cj2l-e796-4ff5-17b729f45577",
        "__uzmf": "7f9000a385f5b1-4246-4c26-9f89-17e1fee3810c172-176899148907914859849417-004d5250dff5ee90c027348",
        "uzmx": "7f90000be9d693-155a-4f0b-8645-155a3bf0813a172-176899148907914859849417-378c322bde9a2c437816",
        "__uzmaj": "a385f5b1-4246-4c26-9f89-17e1fee3810c",
        "__uzmbj": "1782856303",
        "__uzmcj": "173611066485",
        "__uzmdj": "1783849806",
        "__uzmlj": "T6MEtpzY7tq9YQZncEHIpZmZCux9efajlzTdUcHjiyg=",
        "__uzmfj": "7f9000a385f5b1-4246-4c26-9f89-17e1fee3810c3-1782856303547995086676-004335d39a3a272d07e13",
        "dync": "uzmx",
        "uzmxj": "7f90000be9d693-155a-4f0b-8645-155a3bf0813a3-1782856303547995086676-2dc12fc45da90e9934"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Android 16; Mobile; rv:144.0) Gecko/144.0 Firefox/144.0",
        "Referer": "https://www.mako.co.il/mako-vod-live-tv/VOD-6540b8dcb64fd31006.htm",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }

    # "לחיצת היד" מול האתר
    await client.post("https://www.mako.co.il/c99a4269-161c-4242-a3f0-28d44fa6ce24", data=payload, headers=headers)
    
    session_cache["client"] = client
    session_cache["expires_at"] = time.time() + 3600
    return client

@app.get("/api/refresh-stream")
async def refresh_stream():
    try:
        client = await get_valid_client()
        # הכתובת הקבועה של הסטרים
        stream_url = "https://d2249b6f08tjt0.cloudfront.net/k12dvr/master.m3u8"
        
        # משיכת הסטרים
        resp = await client.get(stream_url)
        
        if resp.status_code == 200:
            return {"url": str(resp.url)}
        else:
            # במקרה של שגיאה, נאפס את הסשן כדי שינסה שוב
            session_cache["expires_at"] = 0
            raise HTTPException(status_code=500, detail="Failed to fetch stream")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
