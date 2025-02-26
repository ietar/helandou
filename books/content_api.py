from fastapi import APIRouter, Depends, Body, Request
from pydantic import BaseModel
from models.models import User, Book, BookContent, LevelEnum, Collection

from utils.response import wrap_response, public_wrap_response, r401, r409, r404
from auth import get_user_token, get_user_from_jwt

content_api = APIRouter()


# 不好restful命名了 直接rpc


@content_api.get("/get_all_chapters/{book_id}")
async def all_chapters(book_id: int):
    """
    列出某书籍所有章节的章节名
    :param book_id:
    :return:
    """
    the_book = await Book.get(id=book_id)
    results = await BookContent.filter(book=the_book, deleted=False).order_by("chapter_order") \
        .values("chapter_order", "chapter")
    return wrap_response(results)


class PutContentIn(BaseModel):
    chapter: str
    content: str


class CreateContentIn(BaseModel):
    chapter_order: int
    chapter: str
    content: str


@content_api.post("/create_content/{book_id}")
async def create_content(book_id: int, body: CreateContentIn, token: dict = Depends(get_user_token)):
    """
    创建章节内容
    """
    user_id = token.get("id")
    user = await User.get(id=user_id)
    book = await Book.get_or_none(id=book_id)
    author = await book.author

    if not book:
        return r404(msg="没有该书籍")
    if author != user and user.level < LevelEnum.admin:
        return r401(msg="权限不足 只有作者或管理员用户有权创建章节内容")

    exist = await BookContent.get_or_none(book=book, chapter_order=body.chapter_order)
    if exist:
        return r409(msg="已有该章节")

    new_content = BookContent(**body.model_dump())
    new_content.book = book
    await new_content.save()
    return public_wrap_response(new_content)


@content_api.get("/{book_id}/{chapter_order}")
async def single_content(book_id: int, chapter_order: int):
    """
    获取单章正文
    """
    book1 = await Book.get_or_none(id=book_id, deleted=False)
    if not book1:
        return r404(msg="没有该书籍")

    content = await BookContent.get(book=book1, chapter_order=chapter_order)
    if not content:
        return r404(msg="没有该章节")
    content.read_count += 1
    await content.save()
    return public_wrap_response(content)


@content_api.delete("/{book_id}/{chapter_order}")
async def delete_content(book_id: int, chapter_order: int, token: dict = Depends(get_user_token)):
    """
    删除章节 需要作者本人身份认证
    """
    book1 = await Book.get(id=book_id, deleted=False)
    user_id = token.get("id")
    user = await User.get(id=user_id)
    author = await book1.author

    if not book1:
        return r404(msg="没有该book_id对应的书籍")
    content = await BookContent.get_or_none(book=book1, chapter_order=chapter_order, deleted=False)
    if not content:
        return r404(msg="没有该章节")

    if user.level >= LevelEnum.admin or author == user:
        await content.delete()
        return wrap_response(msg="已成功删除章节")
    else:
        return r401(msg="只有管理员或作者本人有权删除该章节")


@content_api.put("/{book_id}/{chapter_order}")
async def put_content(book_id: int, chapter_order: int, body: PutContentIn, token: dict = Depends(get_user_token)):
    """
    修改章节 需要作者本人身份认证
    """
    book1 = await Book.get(id=book_id)
    if not book1:
        return r404(msg="没有该book_id对应的书籍")
    author = await book1.author
    user_id = token.get("id")
    user = await User.get(id=user_id)
    content = await BookContent.get_or_none(book=book1, chapter_order=chapter_order, deleted=False)
    if not content:
        return r404(msg="没有该章节")

    if user.level >= LevelEnum.admin or author == user:
        await content.update_from_dict(body.dict())
        await content.save()
        return public_wrap_response(msg="已成功修改章节", model=content)
    else:
        return r401(msg="只有管理员或作者本人有权修改该章节")


@content_api.post("/add_to_collection")
async def add_to_collection(content_id: int = Body(embed=True), user=Depends(get_user_from_jwt)):
    content = await BookContent.get_or_none(id=content_id, deleted=False)
    if not content:
        return r404(msg="没有该章节")
    record = await Collection.get_or_none(user=user, content=content)
    if record:
        await record.delete()
        return wrap_response(msg="取消收藏成功")
    else:
        new_collection = await Collection.create(user=user, content=content)
        return public_wrap_response(new_collection, msg="收藏成功")


@content_api.get("/my_collections")
async def get_my_collections(user=Depends(get_user_from_jwt)):
    collections = await Collection.filter(user=user)
    res = []
    for collection in collections:
        content = await collection.content
        book = await content.book
        temp = {"book_id": book.id,
                "book_name": book.book_name,
                "chapter_order": content.chapter_order,
                "chapter": content.chapter,
                "content_id": content.id,
                }
        res.append(temp)

    return wrap_response(res)

