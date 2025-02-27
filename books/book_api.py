# import json
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from models.models import User, Book, LevelEnum

from utils.response import wrap_response, public_wrap_response, r401, r409, r404
from auth import get_user_from_jwt, get_user_token

books_api = APIRouter()


@books_api.get("/my_books")
async def my_books(user=Depends(get_user_from_jwt)):
    """
    获取自己创建的书籍
    """
    books = await Book.filter(author=user, deleted=False)
    return public_wrap_response(books)


@books_api.get("/search")
async def search_books(q=Query()):
    books = await Book.filter(book_name__contains=q, deleted=False).select_related("author").values(
        "id", "book_name", "digest", "read_count",
        "collect_count", "create_time", "update_time",
        author_id="author__id",
        author="author__username"
    )
    return wrap_response(books)


@books_api.get("/")
async def all_books():
    books = await Book.filter(deleted=False).select_related("author").values(
        "id", "book_name", "digest", "read_count",
        "collect_count", "create_time", "update_time",
        author_id="author__id",
        author="author__username"
    )
    return wrap_response(books)


class PutBookIn(BaseModel):
    book_name: str
    digest: str


@books_api.post("/")
async def create_book(body: PutBookIn, token: dict = Depends(get_user_token)):
    if LevelEnum(token.get("level")) < LevelEnum.normal:
        return r401(msg="权限不足 只有通过认证的normal用户有权发表")
    book_name = body.book_name
    exist = await Book.get_or_none(book_name=book_name)
    if exist:
        return r409(msg="已有同名书籍")
    user_id = token.get("id")
    user = await User.get(id=user_id)
    new_book = Book(**body.model_dump())
    new_book.author = user
    await new_book.save()
    return public_wrap_response(new_book, msg="创建书籍成功")


@books_api.get("/{book_id}")
async def single_book(book_id: int):
    book1 = await Book.get_or_none(id=book_id, deleted=False).select_related("author")
    if not book1:
        return r404(msg="没有该书籍")
    author = book1.author
    book1.read_count += 1
    await book1.save()
    res = public_wrap_response(book1)
    res['data']['author'] = author.username
    return res


@books_api.delete("/{book_id}")
async def delete_book(book_id: int, token: dict = Depends(get_user_token)):
    """
    删除书籍 需要作者本人身份认证
    """
    book = await Book.get_or_none(id=book_id, deleted=False)
    if not book:
        return r404(msg="没有该书籍")
    user_id = token.get("id")
    user = await User.get(id=user_id)
    author = await book.author

    if user.level >= LevelEnum.admin or author == user:
        await book.delete()
        return wrap_response(msg="已成功删除书籍")
    else:
        return r401(msg="只有管理员或作者本人有权删除该书籍")


@books_api.put("/{book_id}")
async def put_book(book_id: int, body: PutBookIn, token: dict = Depends(get_user_token)):
    """
    修改书籍 需要作者本人身份认证
    """
    book = await Book.get_or_none(id=book_id, deleted=False)
    if not book:
        return r404(msg="没有该书籍")
    user_id = token.get("id")
    user = await User.get(id=user_id)
    author = await book.author

    if user.level >= LevelEnum.admin or author == user:
        exist = await Book.get_or_none(book_name=body.book_name)
        if exist:
            return r409(msg="已有同名书籍")
        await book.update_from_dict(body.dict())
        await book.save()
        return public_wrap_response(msg="已成功修改书籍", model=book)
    else:
        return r401(msg="只有管理员或作者本人有权修改该书籍")
