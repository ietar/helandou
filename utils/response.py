import datetime
import json
from typing import Optional, List

from fastapi import Response
from tortoise import Model

from utils.models import access_able
from utils.connections import get_redis_connection


def wrap_response(data: Optional[dict | list | Model] = None, success=True, msg=""):
    if isinstance(data, Model):
        data = data.__dict__
    final = {
        "success": success,
        "data": data or {},
        "msg": msg,
    }
    return final


def r429(path: str, next_access: datetime.datetime):
    return Response(
        content=json.dumps(wrap_response(success=False, msg=f"访问{path}过于频繁 下次可访问该地址于{next_access}")),
        status_code=429, media_type="application/json")


def r401(msg="身份识别失败"):
    return Response(content=json.dumps(wrap_response(success=False, msg=msg)),
                    status_code=401, media_type="application/json")


def r409(msg="冲突"):
    return Response(content=json.dumps(wrap_response(success=False, msg=msg)),
                    status_code=409, media_type="application/json")


def r404(msg="找不到"):
    return Response(content=json.dumps(wrap_response(success=False, msg=msg)),
                    status_code=404, media_type="application/json")


def public_wrap_response(model: Model | List[Model], success=True, msg=""):
    """只返回public列 可兼容model: list[Model]"""
    if isinstance(model, list):
        data = [public_response(m) for m in model]
    else:
        data = public_response(model)
    return wrap_response(data, success, msg)


def response_exclude(model: Model, ex: list[str]) -> dict:
    """
    排除模型返回的某些键
    :param model:
    :param ex:
    :return:
    """
    temp = model.__dict__
    for s in ex:
        temp.pop(s)
    return temp


def response_include(model: Model, include: list[str]) -> dict:
    """
    排除模型返回的某些键
    :param model:
    :param include:
    :return:
    """
    temp = model.__dict__
    new = {}
    for s in include:
        new[s] = temp[s]
    return new


def public_response(model: Model) -> dict:
    """
    过滤出科访问的属性字典
    :param model:
    :return:
    """
    slots = access_able(model)
    temp = model.__dict__
    new = {}
    for s in slots:
        new[s] = temp[s]
    return new


async def get_captcha_by_uuid(uuid: str) -> str:
    r = await get_redis_connection(db=0)
    captcha_saved = await r.get(name=f"img_code_{uuid}") or ""
    return captcha_saved.lower()


async def get_email_code_by_uuid(uuid: str) -> str:
    r = await get_redis_connection(db=0)
    captcha_saved = await r.get(name=f"email_code_{uuid}") or ""
    return captcha_saved.lower()

