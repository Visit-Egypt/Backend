from typing import Protocol


from typing import Protocol, Optional

from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse


class UploadRepo(Protocol):
    async def generate_presigned_url(self, upload_req: UploadRequest) -> UploadResponse:
        pass