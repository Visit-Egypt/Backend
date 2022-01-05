

from visitegypt.core.utilities.entities.upload import UploadRequest, UploadResponse

from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from bson import ObjectId
import boto3
import uuid

async def generate_presigned_url(upload_req: UploadRequest) -> UploadResponse:
    # Generate S3 Client
    s3_client = boto3.client(
    's3',
    aws_access_key_id="AKIAZLLK7ARPEHSDFMFH",
    aws_secret_access_key="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")
    content_extension: str = upload_req.content_type.split('/')[1]
    image_id = uuid.uuid4()
    # Generate a Pre-Signed Url Using Boto3
    url = s3_client.generate_presigned_post(Bucket='visitegypt-media-bucket',
                                              Key=f'uploads/{upload_req.resource_name}/{upload_req.resource_id}/{str(image_id)}.{content_extension}',
                                              Fields={
                                                'acl': 'public-read',
                                                'Content-Type': 'image/jpeg'
                                                },
                                                ExpiresIn=3600,
                                                Conditions=[
                                                  {"acl": "public-read"},
                                                  ["starts-with", "$Content-Type", "image/"],
                                              ]
                                          )
    return UploadResponse(**url)