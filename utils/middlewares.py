from datetime import datetime, timedelta
import time
import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI, Request, Response

from settings import throttling_table
from utils.response import r429
from utils.connections import get_redis_connection

DEFAULT_THROTTLING_SECONDS = 1


class ThrottlingMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.request_records: dict[str, dict[str, float]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ip = request.client.host
        path = request.url.path
        current_time = time.time()
        record_ip_dict = self.request_records.get(ip, {})
        record_time = record_ip_dict.get(path, 0)

        if current_time - record_time < throttling_table.get(path, DEFAULT_THROTTLING_SECONDS):
            next_access = datetime.fromtimestamp(record_time) + timedelta(seconds=DEFAULT_THROTTLING_SECONDS)
            return r429(path=path, next_access=next_access)
        else:
            response = await call_next(request)
            self.request_records.setdefault(ip, {})[path] = current_time
            return response


class RedisThrottlingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        path = request.url.path
        ip = request.client.host
        just_let_go = throttling_table.get("just_let_go", [])
        # 白名单直接放行
        for p in just_let_go:
            # print(p, path, re.match(pattern=p, string=path))
            if re.match(pattern=p, string=path):
                response = await call_next(request)
                return response

        # 检查访问记录并更新
        current_time = time.time()
        r = await get_redis_connection(db=1)
        record_time = await r.get(f"{ip}__{path}")
        if record_time:
            next_access = datetime.fromtimestamp(float(record_time)) + timedelta(seconds=DEFAULT_THROTTLING_SECONDS)
            return r429(path=path, next_access=next_access)

        await r.setex(name=f"{ip}__{path}",
                      time=throttling_table.get(path, DEFAULT_THROTTLING_SECONDS) or 60,
                      value=current_time)

        response = await call_next(request)
        return response




