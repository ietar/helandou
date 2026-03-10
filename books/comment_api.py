from collections import defaultdict
from fastapi import APIRouter, Depends
from markdown_it.rules_block import paragraph
from pydantic import BaseModel
from tortoise.expressions import Q
from models.models import User, Book, BookContent, Comment, LevelEnum, CommentAgree

from utils.response import wrap_response, public_wrap_response, r401, r404, r409
from auth import get_user_token, get_user_from_jwt
from settings import custom

comment_api = APIRouter()


# 不好restful命名了 直接rpc

@comment_api.get("/get_all_comments/{chapter_id}")
async def all_comment(chapter_id: int, page: int = 1, per_page: int = 200):
    """
    列出某章节的所有评论（分页+分层结构）
    """
    content = await BookContent.get_or_none(id=chapter_id).prefetch_related("book")
    if not content:
        return r404(msg="没有该章节")

    res = {
        "chapter_comments": [],  # 章评（paragraph=-1）
        "paragraph_comments": defaultdict(list),  # 段评（paragraph>=0）
        "hanging_comments": []  # 悬挂区（paragraph=-2）
    }

    # 使用Q对象构建复杂查询条件
    # base_query = Comment.filter(
    #     Q(book_content=content) &
    #     ~Q(paragraph=-2)  # 排除悬挂区
    # ).select_related("author", "book_content")
    # 只取父评论 子评论后面单独追加
    base_query = Comment.filter(book_content=content, parent_comment=None).select_related("author", "book_content")

    # 分页处理
    total = await base_query.count()
    # 预加载所有关联子评论
    comments = await (base_query.offset((page - 1) * per_page).limit(per_page)
                      .prefetch_related("children").order_by("-agree_count", "create_time"))

    # 分类处理逻辑
    for comment in comments:
        # 悬挂区单独处理
        if comment.paragraph == -2:
            res["chapter_comments"].append(await serialize_comment(comment))
            continue

        # 构建评论树结构
        comment_data = await serialize_comment(comment)
        if comment.children:  #
            comment_data["children"] = [await serialize_comment(c) for c in comment.children]

        # 分类存储
        if comment.paragraph == -1:  # 章评
            res["chapter_comments"].append(comment_data)
        elif comment.paragraph >= 0:  # 段评
            res["paragraph_comments"][comment.paragraph].append(comment_data)

    # 悬挂区单独查询（避免污染主查询） 需书籍作者或管理员
    hanging_comments = Comment.filter(book_content=content, paragraph=-2)
    res["hanging_comments"] = [await serialize_comment(c) for c in await hanging_comments]

    res1 = wrap_response(res)
    res1["meta"] = {"total": total, "page": page, "per_page": per_page}
    return res1


async def serialize_comment(comment: Comment) -> dict:
    """序列化评论数据结构"""
    await comment.fetch_related("author")
    return {
        "id": comment.id,
        "author": {
            "id": comment.author.id,
            "nickname": comment.author.nickname,
            "avatar": comment.author.avatar
        },
        "content": comment.content,
        "paragraph": comment.paragraph,
        "paragraph_digest": comment.paragraph_digest,
        "agree_count": comment.agree_count,
        "create_time": comment.create_time.isoformat(),
        # "is_author": comment.author_id == comment.book_content.book.author_id
    }


class CreateCommentIn(BaseModel):
    content: str
    parent_comment_id: int | None = None
    paragraph: int

@comment_api.post("/create_comment/{chapter_id}")
async def create_comment(chapter_id: int, body: CreateCommentIn,
                         user=Depends(get_user_from_jwt)):
    """
    发表评论
    """
    pid = body.parent_comment_id
    if pid:
        parent = await Comment.get_or_none(id=body.parent_comment_id)
        if not parent:
            return r404(msg="父级评论不存在")

    content = await BookContent.get_or_none(id=chapter_id)
    if not content:
        return r404(msg="没有该章节")
    if user.level < LevelEnum.normal:
        return r401(msg="权限不足 只有通过认证的normal用户有权发表评论")

    new_comment = Comment(**body.model_dump())
    new_comment.book_content = content
    new_comment.author = user
    # 生成并存储digest

    p = body.paragraph
    # 瞎传的都扔给章评
    content_lines = content.content.strip().split("\n")
    if p >= len(content_lines):
        return r409(msg="段落序号超过章节内容范围")
    if p < 0:
         p = -1
    to_digest = content_lines[p]
    new_comment.paragraph_digest = to_digest[:20] if len(to_digest) < 20 else to_digest[:10] + to_digest[-10:]
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
async def delete_comment(comment_id: int, user=Depends(get_user_from_jwt)):
    """
    删除评论 需要作者本人身份认证
    """
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        return r404(msg="没有该评论")
    author = await comment.author

    if user.level >= LevelEnum.admin or author == user:
        await comment.delete()
        return wrap_response(msg="已成功删除评论")
    else:
        # check author 真麻烦吧
        the_content = await comment.book_content
        the_book = await the_content.book
        book_author = await the_book.author
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
        comment.agree_count -= 1
        await comment.save()
        return wrap_response(msg="取消点赞成功")
    else:
        new_record = await CommentAgree.create(user=user, comment=comment)
        comment.agree_count += 1
        await comment.save()
        return public_wrap_response(model=new_record, msg="点赞成功")


class PutCommentIn(BaseModel):
    content: str


@comment_api.put("/{comment_id}")
async def put_comment(comment_id: int, body: PutCommentIn, user=Depends(get_user_from_jwt)):
    """
    修改评论
    """
    return r404(msg="暂不支持修改评论嗷")


class RematchCommentIn(BaseModel):
    new_paragraph: int


@comment_api.post("/rematch_comment/{comment_id}")
async def rematch_comment(comment_id: int, body: RematchCommentIn, user=Depends(get_user_from_jwt)):
    """
    重新关联评论
    """
    comment = await Comment.get(id=comment_id).select_related("book_content__book__author", "children")
    if not (content := comment.book_content):
        return r404(msg="关联章节不存在")
    if not (book := content.book):
        return r404(msg="关联书籍不存在")
    if not (author := book.author):
        return r404(msg="书籍作者不存在")
    if user == author or user.level >= LevelEnum.admin:
        # 评论所在章节所在书籍的作者 或管理员 可重新关联
        comment.paragraph = body.new_paragraph
        # 生成并存储digest
        content_lines = content.content.strip().split("\n")
        if body.new_paragraph >= len(content_lines):
            return r409(msg="段落序号超过章节内容范围")
        to_digest = content_lines[body.new_paragraph]
        new_digest = to_digest[:20] if len(to_digest) < 20 else to_digest[:10] + to_digest[-10:]
        comment.paragraph_digest = new_digest[:20]
        await comment.save()
        children = await comment.children
        if children:  # 一块改了
            await children.update(paragraph_digest=new_digest)
        else:
            pass
        return public_wrap_response(comment, msg="已重新关联")
    else:
        return r409(msg="权限不足，仅该书作者或管理员有权重新关联评论")
