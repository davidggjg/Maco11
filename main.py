import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# הגדרות לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream-manager")

app = FastAPI(title="Maco Stream Manager")

# דשבורד פשוט
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head><title>Maco Manager</title></head>
        <body>
            <h1>מרכז הניהול של מאקו</h1>
            <input type="text" id="vid" value="VOD-6540b8dcb64fd31006" placeholder="הכנס ID סרטון">
            <button onclick="fetchStream()">הפעל</button>
            <div id="result"></div>
            <script>
                async function fetchStream() {
                    const id = document.getElementById('vid').value;
                    document.getElementById('result').innerText = "מטען נתונים...";
                    const res = await fetch('/api/vod/' + id);
                    const data = await res.json();
                    if(data.url) {
                        document.getElementById('result').innerHTML = `<a href="${data.url}" target="_blank">לחץ כאן לצפייה</a>`;
                    } else {
                        document.getElementById('result').innerText = "שגיאה: " + JSON.stringify(data);
                    }
                }
            </script>
        </body>
    </html>
    """

@app.get("/api/vod/{video_id}")
async def get_vod_stream(video_id: str):
    try:
        # כאן אנחנו מריצים את הלוגיקה המשולבת
        final_url = await _fetch_vod_and_validate(video_id)
        return {"type": "vod", "video_id": video_id, "status": "ready", "url": final_url}
    except Exception as e:
        logger.error(f"Error fetching {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _fetch_vod_and_validate(video_id: str) -> str:
    # 1. הכתובת של ה-"לחיצת יד" (ה-POST)
    analytics_url = "https://www.mako.co.il/c99a4269-161c-4242-a3f0-28d44fa6ce24"
    
    # 2. הקישור הסופי (מה-cURL השני)
    stream_url = "https://d2249b6f08tjt0.cloudfront.net/k12dvr/eyJhbGciOiJIUzI1NiJ9.eyJwYXRoIjoiXC9rMTJkdnJcL21hc3Rlci5tM3U4P2ItaW4tcmFuZ2U9MC0xODAwIiwidGltZXN0YW1wIjoxNzgzODQ5ODA4MTcyfQ.m1RdU6VIMwe37bEZior8obbJMEB5DbryzJa1Hld1lhE/playlist_0.m3u8?_uid=16bf0751-776e-4ee5-81e2-974b42b2faf0&rK=b7&_did=18eba19b-0434-b40a-8b33-a4f865d29376"

    # הנתונים שהעתקת מה-cURL (ה-Payload)
    payload = {
        "cid": "cj2l",
        "uzl": "T6MEtpzY7tq9YQZncEHIpZmZCux9efajlzTdUcHjiyg=",
        "et": "85",
        "url": f"https://www.mako.co.il/click/mako-vod-live-tv/{video_id}.htm",
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
        "User-Agent": "Mozilla/5.0 (Android 16; Mobile; rv:144.0) Gecko/144.0 Firefox/144.0",
        "Referer": f"https://www.mako.co.il/mako-vod-live-tv/{video_id}.htm",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }

    # משתמשים ב-Client אחד בשביל לשמור את ה-Session (Cookies)
    async with httpx.AsyncClient() as client:
        # א. מבצעים את ה-POST הראשון
        await client.post(analytics_url, data=payload, headers=headers)
        
        # ב. מבצעים את ה-GET השני (הסשן נשמר)
        resp = await client.get(stream_url, headers=headers)
        
        if resp.status_code == 200:
            return stream_url
        else:
            raise Exception(f"השרת של מאקו חסם אותנו עם סטטוס {resp.status_code}")
