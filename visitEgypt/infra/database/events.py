from fastapi import FastAPI
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from config.environment import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT

class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def get_database() -> AsyncIOMotorClient:
    return db.client



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
