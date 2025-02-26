from fastapi import APIRouter, Response
from fastapi.responses import FileResponse, RedirectResponse
from user.user_api import register_admin

user_pages_router = APIRouter()


@user_pages_router.get("/profile")
def profile_page():
    return FileResponse("static/templates/user/profile.html")


@user_pages_router.get("/register")
def register_page():
    # ok
    return FileResponse("static/templates/user/register.html")


@user_pages_router.get("/login")
def login_page():
    # ok
    return FileResponse("static/templates/user/login.html")


@user_pages_router.get("/forget_password")
def forget_password_page():
    # ok
    return FileResponse("static/templates/user/forget_password.html")


@user_pages_router.get("/reset_password")
def reset_password_page():
    # todo
    return FileResponse("static/templates/user/reset.html")


@user_pages_router.get("/logout")
def logout_page(response: Response):
    # 好像不需要这个页面
    response.delete_cookie(key="username")
    return RedirectResponse(url="/")

