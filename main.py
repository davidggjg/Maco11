# main.py
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Dashboard API is running", "message": "Welcome to the Stream Manager"}

# נתיב לקבלת קישור לשידור חי
@app.get("/api/live/{channel_id}")
def get_live_stream(channel_id: str):
    # כאן נממש את הלוגיקה של ה-Heartbeat בשידור הבא
    return {"type": "live", "channel_id": channel_id, "status": "pending_logic"}

# נתיב לקבלת קישור לסרטון מוקלט (VOD)
@app.get("/api/vod/{video_id}")
def get_vod_stream(video_id: str):
    # כאן נממש את משיכת הטוקן לסרטון ספציפי
    return {"type": "vod", "video_id": video_id, "status": "pending_logic"}
