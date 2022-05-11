from email import message
from typing import List, Optional
from visitegypt.core.base_model import MongoModel, OID
from visitegypt.core.tags.entities.tag import GetTagResponse
from pydantic import BaseModel, Field

class Notification(MongoModel):
    title: str = ''
    description: str = ''
    icon_url: Optional[str] = None
    sent_tags: Optional[List[GetTagResponse]] = []
    sent_users_ids: Optional[List[OID]] = []

class NotificationSaveInDB(Notification):
    sender_id: OID = Field()
    
class NotificationInDB(Notification):
    id: OID = Field()
    


class RegisterDeviceTokenRequest(BaseModel):
    device_token : str = None

class RegisterDeviceTokenResponse(BaseModel):
    message: str = ''

class NotificationSentResponse(BaseModel):
    message: str = ''