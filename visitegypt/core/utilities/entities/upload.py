from email import message
from lib2to3.pgen2.token import OP
from optparse import Option
from typing import Any, List, Optional, Dict
from pydantic import Field
from visitegypt.core.base_model import MongoModel, OID

class UploadRequest(MongoModel):
    user_id:  OID = Field()
    resource_id: OID = Field()
    resource_name: str
    content_type: str

class UploadOptions(MongoModel):
    file_size : Optional[str]
    presigned_url_interval : Optional[str]
    
class UploadResponse(MongoModel):
    url: str
    fields: dict
    options: Optional[UploadOptions]

class UploadConfirmation(MongoModel):
    images_keys : List[str]
    error_images : Optional[List[str]]
    user_id : str

class UploadConfirmationResponse(MongoModel):
    message: str
    status_code: int
