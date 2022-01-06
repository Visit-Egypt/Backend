from visitegypt.config.environment import RESOURCES_NAMES
from visitegypt.core.errors.upload_error import ResourceNotFoundError
from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse
from visitegypt.core.utilities.protocols.upload_repo import UploadRepo
from typing import Optional
from visitegypt.core.utilities.entities.upload import UploadResponse, UploadRequest
from visitegypt.core.utilities.protocols.upload_repo import UploadRepo

from visitegypt.api.container import get_dependencies
repos = get_dependencies()

async def generate_presigned_url(repo: UploadRepo, upload_req: UploadRequest) -> UploadResponse:
    try:
        # Check for the integrity of the coming data.
        # Content Type
        # Resource Name
        if upload_req.resource_name not in RESOURCES_NAMES:
            raise ResourceNotFoundError
        # Resource ID
        if upload_req.resource_name == "users" and upload_req.user_id is not None:
            return await repo.generate_presigned_url(upload_req)
        
    except ResourceNotFoundError as re: raise re


