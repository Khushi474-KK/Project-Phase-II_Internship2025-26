from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.routes import auth_routes, camera_routes, music_routes, frame_analysis_routes, collage_routes
# dataset_service import removed — CSV pipeline is inactive (kept in dataset_service.py for future use)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Camera API",
    description="FastAPI backend for Smart Camera with face detection, age prediction, gender detection, and authentication",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage directory for serving captured images
# Images are stored in backend/storage/images/
backend_dir = os.path.dirname(os.path.dirname(__file__))
storage_path = os.path.join(backend_dir, "storage", "images")
storage_path = os.path.abspath(storage_path)  # Convert to absolute path
os.makedirs(storage_path, exist_ok=True)  # Ensure directory exists
app.mount("/images", StaticFiles(directory=storage_path), name="images")
print(f"✓ Static files mounted: /images -> {storage_path}")

app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(camera_routes.router, prefix="/api/camera", tags=["Camera"])
app.include_router(camera_routes.router, prefix="/api/photos", tags=["Photos"])
app.include_router(music_routes.router, prefix="/api/music", tags=["Music"])
app.include_router(frame_analysis_routes.router, prefix="/api/camera", tags=["Frame Analysis"])
app.include_router(collage_routes.router, prefix="/api/collage", tags=["Collage"])

@app.get("/")
def root():
    return {
        "message": "Smart Camera API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "camera": "/api/camera",
            "music": "/api/music",
            "docs": "/docs"
        }
    }
