from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, RedirectResponse
from user.user_api import register_admin

books_pages_router = APIRouter()


@books_pages_router.get("/create_book")
def create_book():
    return FileResponse("static/templates/books/create_book.html")


@books_pages_router.get("/create_content")
def create_content():
    return FileResponse("static/templates/books/create_content.html")


@books_pages_router.get("/{book_id}")
def single_book(book_id: int):
    return FileResponse("static/templates/books/book.html")


@books_pages_router.get("/")
def all_books():
    return FileResponse("static/templates/books/books.html")

