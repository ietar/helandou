import sys
from typing import Optional
import json
from functools import lru_cache

from fastapi import (FastAPI, WebSocket, WebSocketDisconnect, Request,
                     Response, __version__ as fv, HTTPException)
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

from user.user_api import user_api_router
from user.user_pages import user_pages_router
from books.book_api import books_api
from books.content_api import content_api
from books.comment_api import comment_api
from books.books_pages import books_pages_router
from api.poke_maps import poke_maps_api
from verifications.urls import verification_router
from settings import setting1, custom
from utils.response import wrap_response
from utils.middlewares import ThrottlingMiddleware, RedisThrottlingMiddleware
from utils.connections import get_redis_connection

produce = custom.get("produce", False)
app = FastAPI(docs_url=None, redoc_url=None) if produce else FastAPI()

# api
app.include_router(prefix="/api/user", router=user_api_router, tags=["user"])
app.include_router(prefix="/api/books", router=books_api, tags=["book"])
app.include_router(prefix="/api/content", router=content_api, tags=["content"])
app.include_router(prefix="/api/comment", router=comment_api, tags=["comment"])

app.include_router(prefix="/api/poke_maps", router=poke_maps_api, tags=["poke_maps"])
app.include_router(prefix="", router=verification_router, tags=["verifications"])
# pages
app.include_router(prefix="/user", router=user_pages_router, tags=["user_pages"])
app.include_router(prefix="/books", router=books_pages_router, tags=["books_pages"])

app.mount(path="/static", app=StaticFiles(directory="static"))
register_tortoise(app=app, config=setting1)
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
if custom.get("redis_throttling"):
    app.add_middleware(RedisThrottlingMiddleware)
else:
    app.add_middleware(ThrottlingMiddleware)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@lru_cache(maxsize=16)
@app.get("/anything")
async def anything():
    # todo use redit cache
    data = custom.get("anything")
    return wrap_response(data)


@app.get("/try_redis")
async def try_redis():
    r = await get_redis_connection()
    return wrap_response({"r": str(r)})


# exception handlers
@app.exception_handler(DoesNotExist)
async def does_not_exist_handler(request: Request, exc: DoesNotExist):
    # print(f"{type(exc).__mro__}")
    return Response(content=json.dumps({
        "success": False,
        "data": str(exc),
        "msg": "不存在该实体",
    }), status_code=404, media_type="application/json")


@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    return Response(content=json.dumps({
        "success": False,
        "data": str(exc),
        "msg": exc.detail
    }), status_code=exc.status_code, media_type="application/json")


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return Response(content=json.dumps({
        "success": False,
        "data": str(exc),
        "msg": exc.errors()[0]['msg']  # errors()可能有多种错误 只取第一个作为提示 详情可查看data
    }), status_code=422, media_type="application/json")


@app.exception_handler(Exception)
async def all_exception(request: Request, exc: Exception):
    return Response(content=json.dumps({
        "success": False,
        "data": str(exc),
        "msg": "未被捕获的其他异常"
    }), status_code=500, media_type="application/json")


@app.get("/status", include_in_schema=False)
async def server_status(response: Response, ietar: Optional[str]):
    """
    服务器状态
    :param response:
    :param ietar: /status?ietar
    :return:
    """
    if ietar == "":
        data = {
            "status": "running",
            "fastapi_version": fv,
            "python_version": sys.version_info
        }
        return wrap_response(data)
    else:
        response.status_code = 403
        return wrap_response(success=False, msg="invalid call")


@app.get('/')
async def root(request: Request):
    return FileResponse("static/templates/index.html")


@app.get('/search')
async def search(request: Request):
    return FileResponse("static/templates/search_results.html")


@app.websocket("/ws")
async def ws_test(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(data=f"received: {data}")
    except WebSocketDisconnect:
        pass


# @app.middleware("http")
# async def m2(request: Request, call_next):
#     begin = time.time()
#     print("m2 in")
#     response = await call_next(request)
#     print("m2 out")
#     response.headers["timeit"] = str(time.time() - begin)
#     return response
#
#
# @app.middleware("http")
# async def m1(request: Request, call_next):
#     print("m1 in")
#     response = await call_next(request)
#     print("m1 out")
#     return response


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", port=8080, reload=True)
