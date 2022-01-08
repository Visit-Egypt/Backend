from typing import Any, List, Optional, Dict
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID

class UploadRequest(MongoModel):
    user_id:  OID = Field()
    resource_id: OID = Field()
    resource_name: str
    content_type: str

class UploadResponse(MongoModel):
    url: str
    fields: dict

class UploadConfirmation(MongoModel):
    images_keys : List[str]
    user_id : str