from typing import Optional
from fastapi import APIRouter, status, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.core.utilities.entities.upload import UploadConfirmationResponse, UploadResponse, UploadConfirmation
from visitegypt.core.utilities.services import upload_service
router = APIRouter(responses=generate_response_for_openapi("Upload"))
repo = get_dependencies().upload_repo

"""
@router.post('/',  tags=["Utilities"])
async def upload_request(upload_req: UploadRequest):
    
        The user has to send the upload request with the following data
        {
            "user_id": "",
            "resource_id": "",
            "resource_name": "",
            "content_type":""
        }
    
    try:
        return await upload_service.generate_presigned_url(repo, upload_req)
    except Exception as e: raise e
"""    

# response_model = UploadResponse,

@router.post('/confirm-upload', tags=['Utilities'], response_model= UploadConfirmationResponse)
async def confirm_upload(confirmation_req : UploadConfirmation) -> Optional[UploadConfirmationResponse]:
    try:
        return await upload_service.update_database(repo, confirmation_req)
    except Exception as e:
        raise e
