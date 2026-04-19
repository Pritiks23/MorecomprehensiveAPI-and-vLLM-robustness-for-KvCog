from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as fastapi_app

# Configure CORS for Vercel deployment
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static")
if os.path.exists(static_dir):
    fastapi_app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root redirect to index.html
@fastapi_app.get("/")
async def root():
    from fastapi.responses import FileResponse
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "KV Cognition API - GPU Cost Optimizer"}

# Export for Vercel
app = fastapi_app
