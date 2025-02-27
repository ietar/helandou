# import random
# from typing import Optional
# from datetime import date
import re
import random
import hmac
import datetime
# import time
from hashlib import sha256

from fastapi import APIRouter, Request, Response, Body, Depends, Form
from pydantic import BaseModel, EmailStr, field_validator

from models.models import User, LevelEnum
from utils.response import wrap_response, get_captcha_by_uuid, public_wrap_response, \
    r401, get_email_code_by_uuid, r404
from utils.any import mk_chars, ip2int, hidden_email
from utils.sendmail import send
from settings import custom
from auth import create_user_token, get_user_token, USER_TOKEN_EXPIRE_MINUTES

user_api_router = APIRouter()


@user_api_router.get("/greet")
async def greet():
    counts = await User.filter(deleted=False).count()
    latest = await User.filter(deleted=False).order_by("create_time").last()
    result = {
        "counts": counts,
        "latest": latest.username
    }
    return wrap_response(result)


@user_api_router.post("/send_reset_email")
async def send_reset_email(request: Request, username: str = Form()):
    ip = request.client.host
    user = await User.get_or_none(username=username)
    if not user:
        return r404(msg=f"不存在username为{username}的用户")

    uid = user.id
    email = user.email

    temp = str(random.randint(1, 100000)) + random.choice(username) + random.choice(username)
    user.reset_password_salt = hmac.new(key=bytes(temp, encoding='utf-8'),
                                        msg=bytes(username + str(datetime.datetime.now()), encoding='utf-8'),
                                        digestmod='MD5').hexdigest()
    temp = user.reset_password_salt
    # user.reset_time = timezone.now()
    await user.save()
    m_email = hidden_email(user.email)

    ttl = custom.get('RESET_PASSWORD_EMAIL_TTL_MINUTES', 30)
    host = request.client.host  # todo 为主机地址而非访问ip
    url = f'http://{host}/account/reset?resetsalt={temp}&id={uid}'

    msg = f'''取回密码说明
            {username}， 这封信是由 {host} 发送的。

    您收到这封邮件，是由于这个邮箱地址在 {host} 被登记为用户邮箱， 且该用户请求使用 Email 密码重置功能所致。

    ----------------------------------------------------------------------
    重要！
    ----------------------------------------------------------------------

    如果您没有提交密码重置的请求或不是 {host} 的注册用户，请立即忽略 并删除这封邮件。只有在您确认需要重置密码的情况下，才需要继续阅读下面的 内容。

    ----------------------------------------------------------------------
    密码重置说明
    ----------------------------------------------------------------------

    您只需在提交请求后的 {ttl} 分钟内，通过点击下面的链接重置您的密码：
    {url}
    (如果上面不是链接形式，请将该地址手工粘贴到浏览器地址栏再访问)
    在上面的链接所打开的页面中输入新的密码后提交，您即可使用新的密码登录网站了。您可以在用户控制面板中随时修改您的密码。

    本请求提交者的 IP 为 {ip}

    此致
    {host} 管理团队. {host}
    '''
    # format(username=user.username, host=request.get_host(), ip=ip)
    msg = f"""主题：[重要] 您的{host}账户密码重置指引

    尊敬的{username}：

    您好！本邮件由【{host}】账户安全系统自动发出，为保障您的账户安全，请仔细阅读以下内容。

    ▌安全提示
    ——————————————————————————————
    ⚠️ 若非本人操作：
       • 您近期未申请过密码重置？请立即忽略本邮件
       • 怀疑账户存在异常？请联系客服：support@{host}

    ✅ 安全操作保障：
       • 本链接有效期：{ttl}分钟（北京时间）
       • 请求来源IP：{ip}（如非您常用设备，请提高警惕）

    ▌密码重置指引
    ——————————————————————————————
    1. 点击下方安全链接进入重置页面：
       🔗 <a href="{url}" style="word-break: break-all;">{url}</a>

    2. 在打开的页面中输入新密码（建议组合使用字母+数字+符号）

    3. 完成验证后，即可使用新密码登录

    ▌无法点击链接？
    ——————————————————————————————
    请手动复制以下地址到浏览器地址栏：
    {url}

    ▌技术支持
    ——————————————————————————————
    • 服务时间：每日 9:00-21:00
    • 安全中心：<a href="https://{host}/security">https://{host}/security</a>
    • 紧急冻结账户：<a href="tel:400-123-4567">400-123-4567</a>

    ——————————————————————————————
    此为系统自动邮件，请勿直接回复。
    为确保账户安全，切勿将邮件内容泄露给他人。
    """

    send(to=email, message=msg, subtype="html", title="【荷兰豆】邮箱验证通知 - 重置密码", yourname="荷兰豆")

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


class PutUserIn(BaseModel):
    former_username: str
    former_password: str
    username: str
    password: str
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
async def register(register_user: RegisterUserIn, response: Response):
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

    new_user = User(**temp)
    # new_user.level = LevelEnum.unvalidated
    new_user.level = LevelEnum.normal  # 认证再说吧
    new_user._salt = salt
    await new_user.save()
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
    """给swagger开个后门"""
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
        # todo swagger ui 不装token难用啊
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
        return r401()
    if user.deleted:
        return r401(msg="用户已注销")
    sign = sha256((password + user.get_salt()).encode("utf-8")).hexdigest()
    if sign == user.get_pwd():
        token = create_user_token(data={
            "id": user.id,
            "username": username,
            "level": user.level,
        })
        user.last_login = datetime.datetime.now()
        user.login_ip = ip2int(request.client.host)
        await user.save()

        # ex = time.time() + 60 * USER_TOKEN_EXPIRE_MINUTES
        # response.headers["WWW-Authenticate"] = f"Bearer {token}"
        response.headers["Authorization"] = f"Bearer {token}"
        # 什么玩意 max_age有用 expires怎么给 expires都是session
        response.set_cookie(key="Authorization", value=f"Bearer {token}",
                            # httponly=True,
                            max_age=60 * USER_TOKEN_EXPIRE_MINUTES,
                            # expires=ex)
                            )
        return wrap_response({"token": token})
    else:
        return r401()


@user_api_router.get("/read_user_token")
async def read_user_token(token: dict = Depends(get_user_token)):
    return token


@user_api_router.get("/{user_id}")
async def single_user(user_id: int):
    result = await User.get(id=user_id)
    return public_wrap_response(result)


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


@user_api_router.put("/")
async def put_userinfo(body: PutUserIn):
    body = body.dict()
    username = body.pop("former_username")
    password = body.pop("former_password")
    user = await User.get_or_none(username=username)
    if not user:
        return r401()
    sign = sha256((password + user.get_salt()).encode("utf-8")).hexdigest()
    if sign == user.get_pwd():
        await user.update_from_dict(data=body)
        await user.save()
        return public_wrap_response(user)
    else:
        return r401()

