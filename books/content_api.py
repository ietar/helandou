from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Body, Request, HTTPException
from pydantic import BaseModel
import jwt
from tortoise import transactions, BaseDBAsyncClient
from tortoise.expressions import Q

from models.models import User, Book, BookContent, LevelEnum, Collection, Subscribe, Comment
from settings import custom
from utils.response import wrap_response, public_wrap_response, r401, r409, r404, r402, r400
from utils.coins import subscribe_content_cost
from auth import get_user_token, get_user_from_jwt, oauth2_scheme
from utils.connections import get_redis_connection

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


@content_api.get("/my_collections")
async def get_my_collections(user=Depends(get_user_from_jwt)):
    collections = await Collection.filter(user=user)
    res = []
    for collection in collections:
        content = await collection.content
        book = await content.book
        temp = {"book_id": book.id,
                "book_name": book.book_name,
                # "chapter_order": content.chapter_order,
                "chapter": content.chapter,
                "content_id": content.id,
                }
        res.append(temp)
    return wrap_response(res)


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
            # coins分给作者
            book = await content.book
            author = await book.author
            subscribe_tax = custom.get("subscribe_tax") or 0
            author.coins += Decimal(cost) * Decimal(str(1 - subscribe_tax))
            await author.save()
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
    results = await BookContent.filter(book=the_book, deleted=False).order_by("create_time") \
        .values("id", "chapter")
    return wrap_response(results)

class CreateContentIn(BaseModel):
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

    new_content = BookContent(**body.model_dump())
    new_content.book = book
    await new_content.save()
    book.update_time = new_content.update_time
    await book.save()
    return public_wrap_response(new_content, msg="创建章节成功")


async def handle_read_count(user_id: int, content: BookContent, book: Book):
    r = await get_redis_connection(db=3)
    if await r.get(f"{user_id}__{content.id}"):  # 当天已有浏览该章节记录
        pass
    else:  # 当天未有浏览该章节记录
        content.read_count += 1
        await content.save()
        await r.setex(name=f"{user_id}__{content.id}", value=1, time=3600 * 24)
        r2 = await get_redis_connection(db=4)
        if await r2.get(f"{user_id}__{book.id}"):  # 当天已有浏览该书记录
            pass
        else:  # 没有就记录
            await r2.setex(name=f"{user_id}__{book.id}", value=1, time=3600 * 24)
            book.read_count += 1
            await book.save()
        await r2.close()
    await r.close()


@content_api.get("/{chapter_id}")
async def single_content(chapter_id: int, request: Request):
    """
    获取单章正文
    """
    content = await BookContent.get(id=chapter_id, deleted=False)
    if not content:
        return r404(msg="没有该章节")
    book1 = await content.book
    res = public_wrap_response(content)
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
                # 检验redis
                await handle_read_count(user_id=user.id, content=content, book=book1)
            else:
                res["data"]["need_subscribe"] = True
                res["data"]["content"] = "付费章节，需订阅"
        else:
            # 已订阅用户 或作者
            await handle_read_count(user_id=user.id, content=content, book=book1)
    except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError, HTTPException):
        # 未登录用户
        if content.free:
            pass
        else:
            res["data"]["need_subscribe"] = True
            res["data"]["content"] = "付费章节，需登录并订阅"
    return res


@content_api.delete("/{chapter_id}")
async def delete_content(chapter_id: int, user=Depends(get_user_from_jwt)):
    """
    删除章节 需要作者本人身份认证
    """
    content = await BookContent.get_or_none(id=chapter_id, deleted=False)
    if not content:
        return r404(msg="没有该章节")
    author = await content.book.author
    if user.level >= LevelEnum.admin or author == user:
        await content.delete()
        return wrap_response(msg="已成功删除章节")
    else:
        return r401(msg="只有管理员或作者本人有权删除该章节")


async def rematch_paragraph_digests(content: BookContent, connection_name: Optional[str] = None):
    """
    核心重匹配
    """
    async with transactions.in_transaction(connection_name=connection_name) as conn:
        try:
            # 生成当前章节段落摘要库
            content_lines = content.content.strip().split("\n")
            digests_map = {
                idx: line[:20] if len(line) < 20 else f"{line[:10]}...{line[-10:]}"
                for idx, line in enumerate(content_lines)
            }  # 生成摘要

            # 获取所有关联评论（含子评论）
            comments = await Comment.filter(book_content=content, parent_comment=None).prefetch_related("children")  # 加载子评论
            updates = []

            async def process_comment(comment: Comment, is_top_level: bool = False):
                """处理评论及其子评论"""
                # 原段落匹配逻辑
                original_digest = comment.paragraph_digest
                best_match = None
                for para_idx, digest in digests_map.items():
                    if original_digest == digest:
                        best_match = para_idx
                        break

                # 更新字段
                new_paragraph = best_match if best_match is not None else -2
                new_digest = digests_map.get(best_match, comment.paragraph_digest)  # 匹配上就改摘要 否则保持远样
                if comment.paragraph != new_paragraph or comment.paragraph_digest != new_digest:
                    comment.paragraph = new_paragraph
                    comment.paragraph_digest = new_digest
                    updates.append(comment)

                # 层级控制逻辑
                await comment.fetch_related("children")
                for child in comment.children:
                    # 移除子评论的parent_comment关系
                    if child.parent_comment_id == comment.id:
                        child.parent_comment_id = None
                        updates.append(child)

            # 批量处理主评论
            for c in comments:
                is_top = c.parent_comment_id is None
                await process_comment(c, is_top_level=is_top)

            # 分批次更新（带层级限制）
            batch_size = 500
            total = len(updates)
            for i in range(0, total, batch_size):
                batch = updates[i:i + batch_size]
                await Comment.bulk_update(
                    batch,
                    fields=["paragraph", "paragraph_digest", "parent_comment_id"],  # 新增parent_comment_id字段
                    # using_db=content._meta.db
                )
        except Exception as e:
            conn.rollback()
            return r400(msg=f"评论重新匹配失败 {e}")


class PutContentIn(BaseModel):
    chapter: str
    content: str


@content_api.put("/{chapter_id}")
async def put_content(chapter_id: int, body: PutContentIn, user=Depends(get_user_from_jwt)):
    """
    修改章节 需要作者本人身份认证
    """
    async with transactions.in_transaction() as conn:
        content = await BookContent.get_or_none(id=chapter_id, deleted=False)  # todo
        if not content:
            return r404(msg="没有该章节")
        book = await content.book
        author = await book.author
        if user.level >= LevelEnum.admin or author == user:
            await content.update_from_dict(body.model_dump())
            await content.save()
            # 段评重新匹配
            await rematch_paragraph_digests(content=content, connection_name=conn.connection_name)
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
    still_record = await Collection.filter(~Q(content=content), user=user, content__book=book).exists()  # todo
    async with transactions.in_transaction() as tran:
        if record:
            try:
                await record.delete()
                if not still_record:  # 是最后一个收藏章节
                    book.collect_count -= 1
                    await book.save()
                await tran.commit()
                return wrap_response(msg="取消收藏成功")
            except Exception as e:
                await tran.rollback()
                return r400(msg=str(e))
        else:
            try:
                if not still_record:  # 还未收藏本书章节
                    book.collect_count += 1
                await book.save()
                new_collection = await Collection.create(user=user, content=content)
                await tran.commit()
                return public_wrap_response(new_collection, msg="收藏成功")
            except Exception as e:
                await tran.rollback()
                return r400(msg=str(e))
