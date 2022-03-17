from typing import Dict
from visitegypt.core.chatbot.entities.chatbot import (
    chatBotRes,
    chatBotBase,
)
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import hotels_collection_name,kings_collection_name,restaurants_collection_name,pharmacies_collection_name
from pymongo import ReturnDocument
from bson import ObjectId
from loguru import logger
from visitegypt.infra.errors import InfrastructureException

async def get_city_hotels(city: str):
    try:
        cursor = db.client[DATABASE_NAME][hotels_collection_name].aggregate([{ "$match": { "Governorate": city } },{ "$sample": { "size": 5 }} ])
        row = await cursor.to_list(5)
        if row:
            return row
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)



async def get_king_info(king:str):
    try:
        row = await db.client[DATABASE_NAME][kings_collection_name].find_one(
            {"Name": king}
        )
        if row:
            return row
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_city_restaurants(city: str):
    try:
        cursor = db.client[DATABASE_NAME][restaurants_collection_name].aggregate([{ "$match": { "Governorate": city } },{ "$sample": { "size": 5 }} ])
        row = await cursor.to_list(5)
        if row:
            return row
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_city_pharmacies(city: str):
    try:
        cursor = db.client[DATABASE_NAME][pharmacies_collection_name].aggregate([{ "$match": { "Location": {"$regex" : city} } },{ "$sample": { "size": 5 }} ])
        row = await cursor.to_list(5)
        print(row)
        if row:
            return row
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)