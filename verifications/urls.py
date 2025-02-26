from io import BytesIO
from fastapi import APIRouter, Response, Body

from utils.any import mk_chars, make_default_captcha
from utils.response import wrap_response, r404
from utils.connections import get_redis_connection
from utils.sendmail import send_email_code_password
from settings import custom

verification_router = APIRouter()


@verification_router.get("/image_codes/{uuid}")
async def get_image_code(uuid: str):
    """
    生成图片验证码 返回图片
    """
    chars = mk_chars()
    # print(f"generated chars: {chars}")
    img = make_default_captcha(chars).resize(size=(80, 30))  # 钦定尺寸
    out = BytesIO()
    img.save(out, format="png")
    r = await get_redis_connection(db=0)
    ttl = custom.get("image_capcha_ttl_seconds", 120)
    await r.setex(name=f"img_code_{uuid}", time=ttl, value=chars)
    return Response(content=out.getvalue(), media_type="image/jpg")


@verification_router.get("/get_image_code_by_uuid/{uuid}")
async def get_image_code_by_uuid(uuid: str):
    """
    根据uuid返回图形验证码字符串
    """
    r = await get_redis_connection(db=0)
    code = await r.get(name=f"img_code_{uuid}")
    if not code:
        return r404(msg="图片验证码已过期")
    return wrap_response(data={"code": code})


@verification_router.post("/email_code")
async def post_email_code(uuid: str = Body(), email: str = Body()):
    """
    发送邮件验证码
    """
    length = custom.get("email_code_length", 6)
    chars = mk_chars(length=length)
    r = await get_redis_connection(db=0)
    ttl = custom.get("email_capcha_ttl_seconds", 120)
    await r.setex(name=f"email_code_{uuid}", time=ttl, value=chars)

    send_email_code_password(to=email, code=chars)
    return wrap_response({"data": "已发送"})
