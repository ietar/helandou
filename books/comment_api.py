from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models.models import User, Book, BookContent, Comment, LevelEnum, CommentAgree

from utils.response import wrap_response, public_wrap_response, r401, r409, r404
from auth import get_user_token, get_user_from_jwt
from settings import custom

comment_api = APIRouter()

# 不好restful命名了 直接rpc


@comment_api.get("/get_all_comments/{book_id}/{chapter_order}")
async def all_comment(book_id: int, chapter_order: int):
    """
    列出某章节的所有评论
    """
    book1 = await Book.get_or_none(id=book_id, deleted=False)
    if not book1:
        return r404(msg="没有该章节")
    content = await BookContent.get_or_none(book=book1, chapter_order=chapter_order)
    if not content:
        return r404(msg="没有该章节")

    results = await Comment.filter(book_content=content).order_by("create_time")
    return public_wrap_response(model=results)


class PutCommentIn(BaseModel):
    content: str


class CreateCommentIn(BaseModel):
    content: str
    parent_comment_id: int | None = None


@comment_api.post("/create_comment/{book_id}/{chapter_order}")
async def create_comment(book_id: int, chapter_order: int, body: CreateCommentIn, token: dict = Depends(get_user_token)):
    """
    发表评论
    """
    pid = body.parent_comment_id
    if pid:
        parent = await Comment.get_or_none(id=body.parent_comment_id)
        if not parent:
            return r404(msg="父级评论不存在")

    user_id = token.get("id")
    user = await User.get(id=user_id)
    book1 = await Book.get_or_none(id=book_id, deleted=False)
    if not book1:
        return r404(msg="没有该章节")
    content = await BookContent.get_or_none(book=book1, chapter_order=chapter_order)
    if not content:
        return r404(msg="没有该章节")
    if user.level < LevelEnum.normal:
        return r401(msg="权限不足 只有通过认证的normal用户有权发表评论")

    new_comment = Comment(**body.model_dump())
    new_comment.book_content = content
    new_comment.author = user
    await new_comment.save()
    return public_wrap_response(new_comment)


@comment_api.get("/{comment_id}")
async def single_comment(comment_id: int):
    """
    获取单哥评论详情
    """
    result = await Comment.get_or_none(id=comment_id, deleted=False)
    if not result:
        return r404(msg="没有该评论")
    return public_wrap_response(result)


@comment_api.delete("/{comment_id}")
async def delete_comment(comment_id: int, token: dict = Depends(get_user_token)):
    """
    删除评论 需要作者本人身份认证
    """
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        return r404(msg="没有该评论")
    user_id = token.get("id")
    user = await User.get(id=user_id)
    # check author 真麻烦吧
    author = await comment.author
    the_content = await comment.book_content
    the_book = await the_content.book
    book_author = await the_book.author

    if user.level >= LevelEnum.admin or author == user:
        await comment.delete()
        return wrap_response(msg="已成功删除评论")
    else:
        if custom.get("book_author_can_delete_comment", False) and book_author == user:
            await comment.delete()
            return wrap_response(msg="已成功删除评论")

        return r401(msg="只有管理员或作者本人有权删除该评论")


@comment_api.post("/agree/{comment_id}")
async def agree_comment(comment_id: int, user=Depends(get_user_from_jwt)):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        return r404(msg="评论不存在")
    record = await CommentAgree.get_or_none(user=user, comment=comment)
    if record:
        await record.delete()
        await record.save()
        return wrap_response(msg="取消点赞成功")
    else:
        new_record = await CommentAgree.create(user=user, comment=comment)
        return public_wrap_response(model=new_record, msg="点赞成功")


@comment_api.put("/{book_id}/{chapter_order}")
async def put_comment(book_id: int, chapter_order: int, body: PutCommentIn, token: dict = Depends(get_user_token)):
    """
    修改评论
    """
    return r404(msg="暂不支持修改评论嗷")
    # book1 = await Book.get(id=book_id)
    # if not book1:
    #     return r404(msg="没有该book_id对应的书籍")
    # author = await book1.author
    # user_id = token.get("id")
    # user = await User.get(id=user_id)
    # content = await BookContent.get_or_none(book=book1, chapter_order=chapter_order, deleted=False)
    # if not content:
    #     return r404(msg="没有该章节")
    #
    # if user.level >= LevelEnum.admin or author == user:
    #     await content.update_from_dict(body.dict())
    #     await content.save()
    #     return public_wrap_response(msg="已成功修改章节", model=content)
    # else:
    #     return r401(msg="只有管理员或作者本人有权修改该章节")


