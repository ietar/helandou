import redis.asyncio as redis
from redis import ConnectionError, TimeoutError

# 配置Redis连接
REDIS_URL = "redis://localhost:6379"


# 创建异步Redis连接
async def get_redis_connection(db=0):
    try:
        # r = await redis.from_url(REDIS_URL + f"/{db}", encoding="utf-8", decode_responses=True)
        pool = redis.ConnectionPool(
            host="127.0.0.1",
            port=6379,
            decode_responses=True,
            encoding="utf-8",
            db=db
        )
        r = redis.Redis(connection_pool=pool)
        # print(f"{r = }")
        # sig = await r.ping()
        # print(sig)
        return r
    except ConnectionError:
        print("redis连接错误")
    except TimeoutError:
        print("redis超时")
    except Exception as e:
        print(f"redis异常 {e}")


async def try_redis():
    red = await get_redis_connection()
    await red.set(name="uuid1", value="abcd", ex=600)
    result = await red.get("uuid1")
    print(f"{result = }")
    r2 = await red.get("shit")
    print(f"{r2 =}")

if __name__ == '__main__':
    pass

