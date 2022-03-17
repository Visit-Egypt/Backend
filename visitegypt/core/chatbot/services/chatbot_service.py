from typing import Optional, List
from visitegypt.core.chatbot.entities.chatbot import (
    chatBotRes,
    chatBotBase,
)
from visitegypt.core.chatbot.protocols.chatbot_repo import ChatbotRepo

async def get_hotels_by_city(repo: ChatbotRepo, city: str):
    try:
        hotels = await repo.get_city_hotels(city)
        if hotels:
            return hotels
    except Exception as e:
        raise e

async def get_king_by_name(repo: ChatbotRepo, king: str):
    try:
        king_info = await repo.get_king_info(king)
        if king_info:
            return king_info
    except Exception as e:
        raise e
        
async def get_restaurants_by_city(repo: ChatbotRepo, city: str):
    try:
        restaurants = await repo.get_city_restaurants(city)
        if restaurants:
            return restaurants
    except Exception as e:
        raise e

async def get_pharmacy_by_city(repo: ChatbotRepo, city: str):
    try:
        pharmacies = await repo.get_city_pharmacies(city)
        if pharmacies:
            return pharmacies
    except Exception as e:
        raise e