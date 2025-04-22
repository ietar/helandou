from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.models import User


USER_TOKEN_EXPIRE_MINUTES = 300
USER_TOKEN_EXPIRE_SECONDS = 1
USER_TOKEN_SECRET = "4f5de3cf1e6276d6aca1875e7f69fc3538b152f4612a41532ebd7da48145afad"  # openssl rand -hex 32
ALGO = "HS256"
# oauth2_scheme = OAuth2PasswordBearer("/api/user/login_form")
oauth2_scheme = OAuth2PasswordBearer("/api/user/login")


def create_user_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=USER_TOKEN_EXPIRE_MINUTES)})
    # to_encode.update({"exp": datetime.now(tz=timezone.utc) + timedelta(seconds=USER_TOKEN_EXPIRE_SECONDS)})
    return jwt.encode(payload=to_encode, key=USER_TOKEN_SECRET, algorithm=ALGO)


def get_user_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(jwt=token, key=USER_TOKEN_SECRET, algorithms=ALGO)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="jwt token过期", headers={"WWW-Authenticate": "bearer"})
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail="jwt token签名验证失败", headers={"WWW-Authenticate": "bearer"})
    except Exception as e:
        print(e, type(e))
        raise HTTPException(401, str(e), headers={"WWW-Authenticate": "bearer"})


async def get_user_from_jwt(token: str = Depends(oauth2_scheme)) -> User | None:
    try:
        payload = jwt.decode(jwt=token, key=USER_TOKEN_SECRET, algorithms=ALGO)
        user_id = payload.get("id")
        user = await User.get_or_none(id=user_id)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="jwt token过期", headers={"WWW-Authenticate": "bearer"})
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        raise HTTPException(status_code=401, detail="jwt token签名验证失败", headers={"WWW-Authenticate": "bearer"})
    except Exception as e:
        print(e, type(e))
        raise HTTPException(401, str(e), headers={"WWW-Authenticate": "bearer"})


if __name__ == '__main__':
    r0 = create_user_token({"username": "荷兰豆"})
    print(r0)
    r1 = get_user_token(r0)
    print(r1)
    import time
    time.sleep(1)
    r1 = get_user_token(r0)
    print(r1)
