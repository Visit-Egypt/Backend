from typing import Dict, Protocol
from visitegypt.core.chatbot.entities.chatbot import (
    chatBotRes,
    chatBotBase,
)

class ChatbotRepo(Protocol):
    async def get_city_hotels(city:str):
        pass
    
    async def get_king_info(king:str):
        pass

    async def get_city_restaurants(city:str):
        pass
    
    async def get_city_pharmacies(city:str):
        pass