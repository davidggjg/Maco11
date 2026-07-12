import httpx
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# הגדרות לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream-manager")

app = FastAPI(title="Maco Stream Manager")

# מודלים
class StreamResponse(BaseModel):
    type: str = "vod"
    video_id: str
    status: str
    url: Optional[str] = None

# --- דשבורד פשוט ---
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head><title>Maco Manager</title></head>
        <body>
            <h1>מרכז הניהול של מאקו</h1>
            <input type="text" id="vid" placeholder="הכנס ID סרטון">
            <button onclick="fetchStream()">הפעל</button>
            <div id="result"></div>
            <script>
                async function fetchStream() {
                    const id = document.getElementById('vid').value;
                    const res = await fetch('/api/vod/' + id);
                    const data = await res.json();
                    document.getElementById('result').innerText = JSON.stringify(data);
                }
            </script>
        </body>
    </html>
    """

# --- לוגיקת API ---
@app.get("/api/vod/{video_id}")
async def get_vod_stream(video_id: str):
    try:
        # כאן ה-token מגיע מהפונקציה המקצועית שבתבנית
        token = await _fetch_vod_token(video_id)
        return {"type": "vod", "video_id": video_id, "status": "ready", "url": token}
    except Exception as e:
        logger.error(f"Error fetching {video_id}: {e}")
        raise HTTPException(status_code=500, detail="שגיאה במשיכת הקישור")

async def _fetch_vod_token(video_id: str) -> str:
    # הנה ה-Endpoint וה-Headers שמצאנו ב-cURL שלך
    play_url = "https://d2249b6f08tjt0.cloudfront.net/k12dvr/play" # להחליף אם ה-play endpoint שונה
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Android 16; Mobile; rv:144.0) Gecko/144.0 Firefox/144.0",
        "Referer": "https://www.mako.co.il/mako-vod-live-tv/"
    }
    
    # Payload לדוגמה (אם נדרש)
    payload = {"video_id": video_id}

    async with httpx.AsyncClient(timeout=8.0) as client:
        # בצע את הבקשה
        response = await client.post(play_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # כאן אתה צריך לוודא ששם השדה הוא בדיוק מה שחוזר ב-JSON של מאקו (למשל data["url"])
        return data.get("stream_url", "URL_NOT_FOUND")
