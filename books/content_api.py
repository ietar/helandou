from decimal import Decimal
from fastapi import APIRouter, Depends, Body, Request, HTTPException
from pydantic import BaseModel
import jwt
from tortoise import transactions

from models.models import User, Book, BookContent, LevelEnum, Collection, Subscribe
from utils.response import wrap_response, public_wrap_response, r401, r409, r404, r402, r400
from utils.coins import subscribe_content_cost
from auth import get_user_token, get_user_from_jwt, oauth2_scheme

content_api = APIRouter()


# 不好restful命名了 直接rpc

# @content_api.get("/try_transaction")
# async def try_transaction():
#     user = await User.get(id=1)
#     async with transactions.in_transaction() as tran:
#         user = await User.get(id=1)
#         try:
#             user.coins += 1
#             await user.save()
#             # 1/0
#             await tran.commit()
#             return user
#         except Exception as e:
#             await tran.rollback()
#             return {"exception": str(e)}


@content_api.post("/subscribe/{content_id}")
async def subscribe(content_id: int, user=Depends(get_user_from_jwt)):
    """
    订阅章节
    """
    content = await BookContent.get_or_none(id=content_id)
    if not content:
        return r404(msg="无此章节")
    cost = subscribe_content_cost(content=content.content)
    if user.coins < cost:
        return r402(msg=f"用户余额{user.coins} 不支持该次订阅消耗{cost}")

    record = await Subscribe.get_or_none(user=user, content=content)
    if record:
        # 不允许重复订阅
        return r409(msg="已订阅过该章节")
    # 开启事务
    async with transactions.in_transaction() as tran:
        try:
            res = await Subscribe.create(user=user, content=content)
            user.coins -= Decimal(cost)
            await user.save()
            await tran.commit()
        except Exception as e:
            await tran.rollback()
            return r400(msg=str(e))

    return public_wrap_response(model=res, msg="订阅成功")


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
    free: bool


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
    return public_wrap_response(new_content, msg="创建章节成功")


@content_api.get("/{book_id}/{chapter_order}")
async def single_content(book_id: int, chapter_order: int, request: Request):
    """
    获取单章正文
    """
    book1 = await Book.get_or_none(id=book_id, deleted=False)
    if not book1:
        return r404(msg="没有该书籍")

    content = await BookContent.get(book=book1, chapter_order=chapter_order)
    if not content:
        return r404(msg="没有该章节")

    res = public_wrap_response(content)
    res["data"]["book_id"] = book1.id
    res["data"]["book_name"] = book1.book_name
    res["data"]["cost"] = subscribe_content_cost(content.content)
    res["data"]["need_subscribe"] = False
    res["data"]["can_edit"] = False

    try:
        # 登录用户
        token = await oauth2_scheme(request)  # 显式处理依赖 允许未登录用户访问免费章节
        user = await get_user_from_jwt(token)
        subscribe_record = await Subscribe.get_or_none(user=user, content=content)
        author = await book1.author
        if user == author or user.level >= LevelEnum.admin:  # 编辑权限
            res["data"]["can_edit"] = True
        if not subscribe_record and author != user:
            # 未订阅且非作者
            if content.free:
                content.read_count += 1
                await content.save()
                # return res
            else:
                res["data"]["need_subscribe"] = True
                res["data"]["content"] = "付费章节，需订阅"
                # return res
        else:
            # 已订阅用户 或作者
            content.read_count += 1
            await content.save()
            # return res
    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError, HTTPException):
        # 未登录用户
        if content.free:
            content.read_count += 1
            await content.save()
            # return res
        else:
            res["data"]["need_subscribe"] = True
            res["data"]["content"] = "付费章节，需登录并订阅"
            # return res
    return res


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
    book = await content.book
    record = await Collection.get_or_none(user=user, content=content)
    if record:
        async with transactions.in_transaction() as tran:
            try:
                content.collect_count -= 1
                await content.save()
                book.collect_count -= 1
                await book.save()
                await record.delete()
                await tran.commit()
                return wrap_response(msg="取消收藏成功")
            except Exception as e:
                await tran.rollback()
                return r400(msg=str(e))
    else:
        async with transactions.in_transaction() as tran:
            try:
                content.collect_count += 1
                await content.save()
                book.collect_count += 1
                await book.save()
                new_collection = await Collection.create(user=user, content=content)
                await tran.commit()
                return public_wrap_response(new_collection, msg="收藏成功")
            except Exception as e:
                await tran.rollback()
                return r400(msg=str(e))


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
