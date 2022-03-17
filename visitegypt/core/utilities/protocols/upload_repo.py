from typing import DefaultDict, Protocol


from typing import Protocol, Optional

from visitegypt.core.utilities.entities.upload import UploadConfirmationResponse, UploadRequest, UploadResponse


class UploadRepo(Protocol):
    async def generate_presigned_url(self, upload_req: UploadRequest) -> UploadResponse:
        pass

    async def uploaded_object_urls(self, images_keys: DefaultDict(list), bad_keys: DefaultDict(list), user_id: str) -> Optional[UploadConfirmationResponse]:
        pass