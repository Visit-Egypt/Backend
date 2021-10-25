from logging import log
from aioredis import client
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from ...config.environment import (
    DATABASE_URL,
    MAX_CONNECTIONS_COUNT,
    MIN_CONNECTIONS_COUNT,
    REDIS_HOST, 
    REDIS_PORT

)
from visitegypt.infra.cache.RedisCache import RedisBackend, get_redis


class DataBase:
    client: AsyncIOMotorClient = None

class RedisClient:
    client: RedisBackend = None

db = DataBase()

redis_client = RedisClient()


async def connect_to_db():
    logger.info("Connecting to {0}", repr(DATABASE_URL))

    db.client = AsyncIOMotorClient(
        str(DATABASE_URL),
        minPoolSize=MIN_CONNECTIONS_COUNT,
        maxPoolSize=MAX_CONNECTIONS_COUNT,
    )

    logger.info("Connection established")


async def close_db_connection():
    logger.info("Closing connection to database")

    db.client.close()

    logger.info("Connection closed")


async def connect_to_redis():
    logger.info("Connection to Redis {0}", repr(f"redis://{REDIS_HOST}:{REDIS_PORT}"))
    
    redis_client.client = await RedisBackend.init(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    # logger.info(redis_client.redis_connection)

    logger.info("Connection established to Redis")