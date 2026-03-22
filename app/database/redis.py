import redis.asyncio as redis
from app.config import Config

JTI_EXPIRY = 3600

token_blocklist = redis.Redis.from_url(Config.redis_url)

async def add_jti_blocklist(jti: str) -> None:
    await token_blocklist.set(name= jti, value = "", ex = JTI_EXPIRY)


async def token_in_blocklist(jti:str) -> bool:
    jti = await token_blocklist.get(jti)

    if jti is not None:
        return True
    else:
        return False