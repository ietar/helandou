from datetime import datetime, timedelta
import time
import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI, Request, Response

from settings import throttling_table, custom
from utils.response import r429
from utils.connections import get_redis_connection

DEFAULT_THROTTLING_SECONDS = custom.get("DEFAULT_THROTTLING_SECONDS") or 1  # 默认间隔1秒即允许访问


class RedisThrottlingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        ip = request.client.host
        table = throttling_table.copy()
        just_let_go = table.pop("just_let_go")
        # 检查自定义时间间隔限流名单
        for p,v in table.items():
            if re.match(pattern=p, string=path):
                # 检查访问记录并更新
                current_time = time.time()
                r = await get_redis_connection(db=1)
                record_time = await r.get(f"{ip}__{path}")
                if record_time:
                    next_access = datetime.fromtimestamp(float(record_time)) + timedelta(seconds=v)
                    return r429(path=path, next_access=next_access)

                await r.setex(name=f"{ip}__{path}",
                              time=v,
                              value=current_time)
                response = await call_next(request)
                return response
        # 白名单直接放行
        for p in just_let_go:
            if re.match(pattern=p, string=path):
                response = await call_next(request)
                return response
        # 其他按默认时间间隔
        current_time = time.time()
        r = await get_redis_connection(db=1)
        record_time = await r.get(f"{ip}__{path}")
        if record_time:
            next_access = datetime.fromtimestamp(float(record_time)) + timedelta(seconds=DEFAULT_THROTTLING_SECONDS)
            return r429(path=path, next_access=next_access)

        await r.setex(name=f"{ip}__{path}",
                      time=DEFAULT_THROTTLING_SECONDS,
                      value=current_time)

        response = await call_next(request)
        return response



# class ThrottlingMiddleware(BaseHTTPMiddleware):
#
#     def __init__(self, app: FastAPI, *args, **kwargs):
#         super().__init__(app, *args, **kwargs)
#         self.request_records: dict[str, dict[str, float]] = {}
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         ip = request.client.host
#         path = request.url.path
#         current_time = time.time()
#         record_ip_dict = self.request_records.get(ip, {})
#         record_time = record_ip_dict.get(path, 0)
#
#         if current_time - record_time < throttling_table.get(path, DEFAULT_THROTTLING_SECONDS):
#             next_access = datetime.fromtimestamp(record_time) + timedelta(seconds=DEFAULT_THROTTLING_SECONDS)
#             return r429(path=path, next_access=next_access)
#         else:
#             response = await call_next(request)
#             self.request_records.setdefault(ip, {})[path] = current_time
#             return response







