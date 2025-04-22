import os
import shutil
import json
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ai import analyze_video_for_explicit_content  # Import the analysis function

app = FastAPI()

MEDIA_DIR = "media/videos"
MARKER_FILE = "markers.json"
os.makedirs(MEDIA_DIR, exist_ok=True)

# Mount static files
app.mount("/media/videos", StaticFiles(directory=MEDIA_DIR), name="media")

# Jinja templates
templates = Jinja2Templates(directory="templates")

# Load or initialize markers
if os.path.exists(MARKER_FILE):
    with open(MARKER_FILE, "r") as f:
        markers = json.load(f)
else:
    markers = {}

@app.get("/admin", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("uploadform.html", {"request": request})

@app.post("/admin/upload")
async def upload_video(title: str = Form(...), file: UploadFile = File(...)):
    file_location = os.path.join(MEDIA_DIR, file.filename)
    
    # Save the uploaded file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get NSFW timestamps for the uploaded video
    skip_times = analyze_video_for_explicit_content(file_location)

    # Save skip timestamps to markers dictionary
    markers[file.filename] = skip_times

    # Save markers to a JSON file
    with open(MARKER_FILE, "w") as f:
        json.dump(markers, f)

    return {"message": "Video uploaded successfully", "filename": file.filename, "markers": skip_times}

@app.get("/markers/{filename}")
async def get_markers(filename: str):
    return JSONResponse(content=markers.get(filename, []))

@app.get("/player", response_class=HTMLResponse)
async def list_videos(request: Request):
    video_files = os.listdir(MEDIA_DIR)
    video_names = [video for video in video_files if video.endswith(".mp4")]
    return templates.TemplateResponse("list_videos.html", {"request": request, "videos": video_names})

@app.get("/play/{filename}", response_class=HTMLResponse)
async def play_video(request: Request, filename: str):
    return templates.TemplateResponse("player.html", {"request": request, "filename": filename})

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
