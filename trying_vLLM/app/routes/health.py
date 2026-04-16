
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
import os

router = APIRouter()

@router.get("/")
async def root():
	return RedirectResponse(url="/ui")

@router.get("/ui")
async def ui():
	"""Serve the UI page"""
	html_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
	with open(html_path, "r") as f:
		return HTMLResponse(content=f.read())

@router.get("/health")
async def health():
	return {"status": "ok"}
