

from visitegypt.core.accounts.entities.user import UserUpdate
from visitegypt.core.posts.entities.post import UpdatePost
from visitegypt.core.utilities.entities.upload import UploadConfirmation, UploadRequest, UploadResponse
from visitegypt.infra.database.repositories import user_repository, post_repository
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_ACCESS_KEY_ID
import boto3
import uuid
from typing import DefaultDict, List

async def generate_presigned_url(upload_req: UploadRequest) -> UploadResponse:
    # Generate S3 Client
    s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    content_extension: str = upload_req.content_type.split('/')[1]
    image_id = uuid.uuid4()
    # Generate a Pre-Signed Url Using Boto3
    url = s3_client.generate_presigned_post(Bucket=AWS_S3_BUCKET_NAME,
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


async def uploaded_object_urls(images_keys: DefaultDict(list), user_id: str) -> bool:
  try:
    if images_keys.get('users') != None and len(images_keys.get('users')) > 0:
      user_image : str = f'https://{AWS_S3_BUCKET_NAME}.s3.us-west-2.amazonaws.com/{images_keys.get("users")[0]}'
      # user_id : str = images_keys.get('users')[0].split('/')[2]
      await user_repository.update_user(UserUpdate(photo_link=user_image), user_id)
    
    if images_keys.get('posts') != None and len(images_keys.get('posts')) > 0:
      post_images : List = [f'https://{AWS_S3_BUCKET_NAME}.s3.us-west-2.amazonaws.com/{image}' for image in images_keys.get('posts')]
      post_id : str = images_keys.get('posts')[0].split('/')[2]

      updated_post : UpdatePost = UpdatePost(list_of_images = post_images)
      await post_repository.update_post(updated_post, post_id, user_id)
  except Exception as e: raise e