# import random
# from typing import Optional
# from datetime import date
import re
import random
import hmac
import datetime
import time
from hashlib import sha256

from fastapi import APIRouter, Request, Response, Body, Depends, Form
from pydantic import BaseModel, EmailStr, field_validator

from models.models import User, LevelEnum
from utils.response import wrap_response, get_captcha_by_uuid, public_wrap_response, \
    r401, get_email_code_by_uuid, r404, public_response, r409
from utils.any import mk_chars, ip2int, hidden_email, int2ip
from utils.sendmail import send_email_code_for_reset_password
from settings import custom
from auth import create_user_token, get_user_token, USER_TOKEN_EXPIRE_MINUTES, get_user_from_jwt
from utils.connections import get_redis_connection

user_api_router = APIRouter()


@user_api_router.post("/vivo50")
async def vivo50(user=Depends(get_user_from_jwt)):
    """通过首页vivo50渠道每日领币"""
    r = await get_redis_connection(db=2)
    if await r.get(f"vivo50__{user.id}"):
        return wrap_response(success=False, msg="24h内已有领币记录")
    amount = random.randint(20, 50)
    await r.setex(name=f"vivo50__{user.id}", value=time.time(), time=60*60*24)
    user.coins += amount
    await user.save()
    return wrap_response({"amount": amount})


@user_api_router.get("/greet")
async def greet():
    counts = await User.filter(deleted=False).count()
    latest = await User.filter(deleted=False).order_by("create_time").last()
    result = {
        "counts": counts,
        "latest": latest.username
    }
    return wrap_response(result)


@user_api_router.post("/reset_password")
async def reset_password(reset_password_salt: str = Form(),
                         user_id: int = Form(), password: str = Form(), re_password: str = Form()):
    if password != re_password:
        return r409(msg="两次输入密码不一致")
    target_user = await User.get(id=user_id)
    ttl = custom.get('RESET_PASSWORD_EMAIL_TTL_MINUTES', 10)
    if target_user.reset_password_salt == reset_password_salt:
        if datetime.datetime.now(datetime.UTC) - target_user.reset_time < datetime.timedelta(minutes=ttl):
            target_user.set_pwd(pwd=password)
            # print(password, target_user.get_pwd())
            await target_user.save()
            return wrap_response(msg=f'已成功重置密码，请重新登录')

    return r401()


@user_api_router.post("/send_reset_email")
async def send_reset_email(request: Request, username: str = Form()):
    ip = request.client.host
    user = await User.get_or_none(username=username)
    if not user:
        return r404(msg=f"不存在username为{username}的用户")

    uid = user.id
    email = user.email

    temp = str(random.randint(1, 100000)) + random.choice(username) + random.choice(username)
    user._reset_password_salt = hmac.new(key=bytes(temp, encoding='utf-8'),
                                        msg=bytes(username + str(datetime.datetime.now()), encoding='utf-8'),
                                        digestmod='MD5').hexdigest()
    temp = user.reset_password_salt
    user.reset_time = datetime.datetime.now()
    await user.save()
    m_email = hidden_email(user.email)

    ttl = custom.get('RESET_PASSWORD_EMAIL_TTL_MINUTES', 10)
    host = custom.get("host_url") or "127.0.0.1:8080"
    url = f'http://{host}/user/reset_password?reset_salt={temp}&id={uid}'
    send_email_code_for_reset_password(to=email, username=username, url=url, ip=ip, ttl=ttl)

    return wrap_response(msg=f'已成功发送找回邮件至 {m_email}')


@user_api_router.get("/user_exist")
async def user_exist(username: str):
    user = await User.get_or_none(username=username)
    if not user:
        return wrap_response({"data": "未注册"})
    else:
        return wrap_response(success=False, msg="用户名重复")


@user_api_router.get("/nothing")
async def nothing(request: Request):  # test
    print(request.cookies, request.client.host)
    return wrap_response({})


@user_api_router.get("/")
async def all_users():
    results = await User.filter(deleted=False)
    return public_wrap_response(results)


class RegisterUserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    mobile: str
    captcha: str
    email_code: str
    uuid: str

    @field_validator('mobile')
    def validate_phone(cls, v):  # 别问 写self报错
        if v is not None:
            # 假设手机号格式为 +<国家码><手机号> 或 <手机号>，其中手机号为10位数字
            pattern = re.compile(r'^1[3-9]\d{9}$')  # 国内
            # pattern = re.compile(r'^\+?[1-9]\d{1,14}$')  # 国际
            if not pattern.match(v):
                raise ValueError('手机号格式不正确')
        return v


@user_api_router.post("/register_admin")
async def register_admin(register_user: RegisterUserIn, response: Response):
    """
    唯一管理员用户注册
    """
    find_user = await User.filter(level=LevelEnum.admin)
    if find_user:
        response.status_code = 409
        return wrap_response(success=False, msg="管理员用户已存在")

    temp = register_user.model_dump()
    pwd = temp.pop("password")
    salt = mk_chars(length=6)
    temp["_password"] = sha256((pwd + salt).encode("utf-8")).hexdigest()

    new_user = User(**temp)
    new_user.level = LevelEnum.admin
    new_user._salt = salt
    await new_user.save()
    return public_wrap_response(new_user)


@user_api_router.post("/register")
async def register(request: Request, register_user: RegisterUserIn, response: Response):
    """
    普通用户注册
    """
    find_user = await User.filter(username=register_user.username) or await User.filter(mobile=register_user.mobile)
    if find_user:  # 用户已存在
        response.status_code = 409
        return wrap_response(success=False, msg="用户名或手机号重复")

    saved_chars = await get_captcha_by_uuid(register_user.uuid)
    auto_captcha = custom.get("auto_captcha")
    if saved_chars != register_user.captcha and register_user.captcha != auto_captcha:
        return r401(msg="图形验证码错误")
    saved_email_code = await get_email_code_by_uuid(register_user.uuid)
    if saved_email_code != register_user.email_code and register_user.email_code != auto_captcha:
        return r401(msg="邮件验证码错误")

    temp = register_user.model_dump()
    pwd = temp.pop("password")
    salt = mk_chars(length=6)
    temp["_password"] = sha256((pwd + salt).encode("utf-8")).hexdigest()
    temp["nickname"] = f"用户{register_user.username}的昵称"
    new_user = User(**temp)
    # 顺便登录
    new_user.level = LevelEnum.normal  # 认证再说吧
    new_user._salt = salt
    new_user.last_login = datetime.datetime.now()
    new_user.login_ip = ip2int(request.client.host)
    await new_user.save()
    token = create_user_token(data={
        "id": new_user.id,
        "username": new_user.username,
        "level": new_user.level,
        "nickname": new_user.nickname,
    })
    response.set_cookie(key="Authorization", value=f"Bearer {token}", max_age=60 * USER_TOKEN_EXPIRE_MINUTES)
    return public_wrap_response(new_user)


@user_api_router.post("/change_level")
async def change_level(target_user_id: int = Body(), target_level: LevelEnum = Body(),
                       token: dict = Depends(get_user_token)):
    # print(target_user_id)
    if LevelEnum(token.get("level")) < LevelEnum.admin:
        return r401(msg="权限不足 只有admin用户有权更改用户等级")
    user = await User.get(id=target_user_id)
    user.level = target_level
    await user.save()
    return public_wrap_response(user)


class LoginBody(BaseModel):
    username: str
    password: str
    uuid: str
    image_code: str


@user_api_router.post("/login_form", include_in_schema=False)
async def login2(response: Response, username=Form(), password=Form()):
    """
    给swagger开个后门
    不太行 swagger_ui不会自己装header
    """
    user = await User.get_or_none(username=username)
    if not user:
        return r401()
    sign = sha256((password + user.get_salt()).encode("utf-8")).hexdigest()
    if sign == user.get_pwd():
        token = create_user_token(data={
            "id": user.id,
            "username": username,
            "level": user.level,
        })
        # swagger ui 不装token难用啊
        response.headers["Authorization"] = f"Bearer {token}"
        # response.set_cookie(key="WWW-authenticate", value=f"Bearer {token}", httponly=True)
        return wrap_response({"token": token})
    else:
        return r401()


@user_api_router.post("/login")
async def login(request: Request, response: Response, body: LoginBody):
    username = body.username
    password = body.password
    uuid = body.uuid
    image_code = body.image_code

    saved_chars = await get_captcha_by_uuid(uuid)
    auto_captcha = custom.get("auto_captcha")
    if saved_chars != image_code and image_code != auto_captcha:
        return r401(msg="图形验证码错误")

    user = await User.get_or_none(username=username)
    if not user:
        return r401(msg="无此用户")
    if user.deleted:
        return r401(msg="用户已注销")
    # sign = sha256((password + user.get_salt()).encode("utf-8")).hexdigest()
    sign = user.make_pwd(pwd=password)
    if sign == user.get_pwd():
        token = create_user_token(data={
            "id": user.id,
            "username": username,
            "level": user.level,
            "nickname": user.nickname,
        })
        user.last_login = datetime.datetime.now()
        user.login_ip = ip2int(request.client.host)
        await user.save()
        response.set_cookie(key="Authorization", value=f"Bearer {token}",max_age=60 * USER_TOKEN_EXPIRE_MINUTES)
        return wrap_response({"token": token})
    else:
        return r401()


@user_api_router.get("/read_user_token")
async def read_user_token(token: dict = Depends(get_user_token)):
    return token


@user_api_router.get("/{user_id}")
async def single_user(user_id: int, user=Depends(get_user_from_jwt)):
    query_user = await User.get(id=user_id)
    books = await query_user.books

    if user.level < LevelEnum.admin and user.id != user_id:
        # 仅获取部分信息 username id level books
        data = {
            "username": query_user.username,
            "id": query_user.id,
            "level": query_user.level,
            "books": [public_response(book) for book in books]
        }
        return wrap_response(data)

    else:
        # 获取全部信息
        data = public_response(query_user)
        data["login_ip"] = int2ip(data["login_ip"])
        data["books"] = [public_response(book) for book in books]
        return wrap_response(data)


@user_api_router.delete("/{user_id}")
# async def delete_user(body: LoginBody, token: dict = Depends(get_user_token)):
async def delete_user(body: LoginBody):
    """
    注销用户 需要再次确认密码 只允许注销自己嗷
    """
    # print(token)
    username = body.username
    password = body.password
    user = await User.get(username=username)
    sign = sha256((password + user.get_salt()).encode("utf-8")).hexdigest()

    if sign == user.get_pwd():
        user.deleted = True
        await user.save()
        return wrap_response(msg="已成功注销用户")
    else:
        return r401()


class PutUserIn(BaseModel):
    # former_username: str
    nickname: str
    former_password: str
    # username: str
    new_password: str  # 绝了 就是不能叫_password
    email: EmailStr
    mobile: str

    @field_validator('mobile')
    def validate_phone(cls, v):  # 别问 写self报错
        if v is not None:
            # 假设手机号格式为 +<国家码><手机号> 或 <手机号>，其中手机号为10位数字
            pattern = re.compile(r'^1[3-9]\d{9}$')  # 国内
            # pattern = re.compile(r'^\+?[1-9]\d{1,14}$')  # 国际
            if not pattern.match(v):
                raise ValueError('手机号格式不正确')
        return v


@user_api_router.put("/")
async def put_userinfo(body: PutUserIn, user=Depends(get_user_from_jwt)):
    body = body.model_dump()

    former_password = body.pop("former_password")
    if user.get_pwd() == user.make_pwd(former_password):
        if body["new_password"]:  # 传新密码才改 否则不改
            user.set_pwd(body.pop("new_password"))

        await user.update_from_dict(data=body).save()  # password可为空 即不更新
        await user.save()
        # print(user.get_pwd())
        return public_wrap_response(user, msg="更新用户信息成功")
    else:
        return r401(msg="旧密码输入错误")

