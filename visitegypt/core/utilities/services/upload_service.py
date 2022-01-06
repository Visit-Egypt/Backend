from visitegypt.config.environment import RESOURCES_NAMES
from visitegypt.core.errors.upload_error import ResourceNotFoundError
from visitegypt.core.utilities.entities.upload import UploadConfirmation, UploadRequest, UploadResponse
from visitegypt.core.utilities.protocols.upload_repo import UploadRepo
from typing import DefaultDict, Optional
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


async def update_database(repo: UploadRepo, upload_confirmation: UploadConfirmation) -> bool:
    try:
        # Filter Array to Dict
        dict_of_resources = DefaultDict(list)
        for image in upload_confirmation.images_keys:
            splitted_image = image.split('/')
            dict_of_resources[splitted_image[1]].append(image)
        return await repo.uploaded_object_urls(dict_of_resources)
    except Exception as e:
        raise e
