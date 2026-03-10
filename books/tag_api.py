from fastapi import APIRouter, Body, Depends
from models.models import Tag, LevelEnum
from utils.response import public_wrap_response, r401, wrap_response
from auth import get_user_from_jwt
tags_api = APIRouter()


@tags_api.get("/")
async def get_tags():
    return public_wrap_response(await Tag.all())


@tags_api.post("/")
async def create_tag(tag_name: str = Body(embed=True), user=Depends(get_user_from_jwt)):
    if user.level < LevelEnum.root:
        return r401(msg="仅root用户可操作")
    new_tag = await Tag.create(tag_name=tag_name)
    return public_wrap_response(new_tag)


@tags_api.put("/{tag_id}")
async def put_tag(tag_id: int, tag_name: str = Body(embed=True), user=Depends(get_user_from_jwt)):
    if user.level < LevelEnum.root:
        return r401(msg="仅root用户可操作")
    tag = await Tag.get(id=tag_id)
    tag.tag_name = tag_name
    await tag.save()
    return public_wrap_response(tag)


@tags_api.delete("/{tag_id}")
async def delete_tag(tag_id: int, user=Depends(get_user_from_jwt)):
    if user.level < LevelEnum.root:
        return r401(msg="仅root用户可操作")
    tag = await Tag.get(id=tag_id)
    await tag.delete()
    return wrap_response(msg="已删除该tag")
