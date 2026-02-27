from fastapi import APIRouter
from fastapi.responses import FileResponse
content_pages_router = APIRouter()

@content_pages_router.get("/{chapter_id}")
def book_content(chapter_id: int):
    return FileResponse("static/templates/books/content.html")