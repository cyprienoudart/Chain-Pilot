"""
Dashboard Routes - Phase 5
Serve the web dashboard interface
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Phase 5: Dashboard"])

# Get dashboard directory path
DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
STATIC_DIR = DASHBOARD_DIR / "static"


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard():
    """Serve the main dashboard HTML"""
    index_file = TEMPLATES_DIR / "index.html"
    
    if not index_file.exists():
        return HTMLResponse(
            content="<h1>Dashboard not found</h1><p>Please ensure dashboard files are installed.</p>",
            status_code=404
        )
    
    with open(index_file, 'r') as f:
        content = f.read()
    
    logger.info("Serving dashboard")
    return HTMLResponse(content=content)


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard_alt():
    """Alternative route to serve dashboard"""
    return await serve_dashboard()


@router.get("/static/{file_path:path}", include_in_schema=False)
async def serve_static_files(file_path: str):
    """Serve static files (CSS, JS, images)"""
    file = STATIC_DIR / file_path
    
    if not file.exists() or not file.is_file():
        return HTMLResponse(content="File not found", status_code=404)
    
    # Determine content type
    content_type = "text/plain"
    if file_path.endswith('.css'):
        content_type = "text/css"
    elif file_path.endswith('.js'):
        content_type = "application/javascript"
    elif file_path.endswith('.json'):
        content_type = "application/json"
    elif file_path.endswith('.png'):
        content_type = "image/png"
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        content_type = "image/jpeg"
    elif file_path.endswith('.svg'):
        content_type = "image/svg+xml"
    
    return FileResponse(file, media_type=content_type)

