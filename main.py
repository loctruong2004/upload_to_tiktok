from fastapi import FastAPI, Form
from pydantic import BaseModel
from src.tiktok_uploader.upload import upload_video
import uvicorn

app = FastAPI()

@app.post("/upload")
async def upload_tiktok(
    video_path: str = Form(...),
    description: str = Form(...)
):
    try:
        # Gọi hàm upload TikTok
        upload_video(
            video_path,
            description=description,
            cookies="cookies.txt"
        )
        return {"status": "success", "message": f"Video {video_path} uploaded successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# dowload video from youtube
import yt_dlp
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import List
import os
import subprocess

DOWNLOAD_DIR = "downloads"
SPLIT_DIR = "splits"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(SPLIT_DIR, exist_ok=True)

# SCOPES = ['https://www.googleapis.com/auth/drive.file']

class VideoRequest(BaseModel):
    title: str
    description: str
    urlvideo: str

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def split_video(input_path: str, output_prefix: str, segment_duration: int = 100) -> List[str]:
    output_base = os.path.join(SPLIT_DIR, output_prefix)
    os.makedirs(output_base, exist_ok=True)

    output_pattern = os.path.join(output_base, f"{output_prefix}_%03d.mp4")

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(segment_duration),
        "-reset_timestamps", "1",
        output_pattern
    ]

    try:
        subprocess.run(cmd, check=True)
        output_files = sorted([
            os.path.join(output_base, f)
            for f in os.listdir(output_base)
            if f.endswith(".mp4")
        ])
        return output_files
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to split video: {e}")
@app.post("/download")
async def download_video(data: VideoRequest):
    title = data.title
    description = data.description
    url = data.urlvideo
    safe_title = sanitize_filename(title)
    output_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

    try:
        # Lấy thông tin video trước
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)  # giây

        # Nếu dài hơn 30 phút thì không cho tải
        if duration > 1800:
            return JSONResponse(
                status_code=400,
                content={"error": "Video dài hơn 30 phút, không thể tải."}
            )

        print("Bắt đầu tải video...")
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bv*+ba/best',
            'merge_output_format': 'mp4',
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Đã tải xong.")

        print("Bắt đầu cắt video...")
        segment_files = split_video(output_path, safe_title, segment_duration=150)
        print(f"Đã cắt video thành {len(segment_files)} đoạn.")

        # Trả về mảng JSON duy nhất
        segments_info = [
            {
                "index": idx + 1,
                "path": seg_path,
                "filename": os.path.basename(seg_path),
                "url": url,
                "description": description
            }
            for idx, seg_path in enumerate(segment_files)
        ]

        return JSONResponse(content=segments_info)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    # Chạy server FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)
