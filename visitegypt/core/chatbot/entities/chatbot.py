from typing import List, Optional
from pydantic import Field
from starlette import responses
from visitegypt.core.base_model import MongoModel, OID

class chatBotBase(MongoModel):
    message:str
class chatBotRes(MongoModel):
    response:str