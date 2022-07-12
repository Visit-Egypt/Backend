from datetime import datetime
import json
from typing import Optional, List, Dict
from visitegypt.core.utilities.entities.notification import (
    Notification,
    NotificationSaveInDB,
    NotificationsPageResponse
)
from visitegypt.core.accounts.entities.user import UserUpdate
from visitegypt.infra.database.utils import calculate_start_index, check_has_next,check_next

from visitegypt.config.environment import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_NOTIFICATION_PLATFORM_ARN, AWS_NOTIFICATION_TOPIC_ARN
from bson import ObjectId
import boto3
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import notifications_collection_name
from visitegypt.infra.errors import InfrastructureException
from visitegypt.core.errors.notifications_error import NotificationNotFoundError

from loguru import logger

async def get_sns_client():
    return boto3.client \
        (
            'sns',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name = 'us-east-1'
        )
async def register_device_token(user_id: str, device_token: str) -> bool:
    try:
        # Generate an Endpoint to this user and also add the token to the DB
        # Add Device Token to the user DB
        sns_client = await get_sns_client()
        device_endpoint = sns_client.create_platform_endpoint(
            PlatformApplicationArn=AWS_NOTIFICATION_PLATFORM_ARN,
            Token=device_token,
            CustomUserData=user_id
        )
        # Subscribe to the topic
        response = sns_client.subscribe(
            TopicArn=AWS_NOTIFICATION_TOPIC_ARN,
            Protocol='application',
            Endpoint=device_endpoint.get('EndpointArn'),
            ReturnSubscriptionArn=True
        )

        if response.get('SubscriptionArn'):
            from visitegypt.infra.database.repositories.user_repository import update_user
            result = await update_user(updated_user=UserUpdate(device_token = device_token, device_arn_endpoint = device_endpoint.get('EndpointArn')), user_id = user_id)
            if result:
                return True
        return False
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def send_notification(notification: Notification, sender_id: ObjectId) -> bool:
    try:
        title = notification.title
        msg = notification.description
        gcm_msg_json = json.dumps({
            'notification': {
                "title": title, 
                "body": msg,
                "icon": notification.icon_url
            }
        })

        msg_to_be_sent = {
            'default': msg,
            'GCM': gcm_msg_json
        }
        sns_client = await get_sns_client()
        res = sns_client.publish(TopicArn=AWS_NOTIFICATION_TOPIC_ARN, Message=json.dumps(msg_to_be_sent), MessageStructure='json')
        if res.get('MessageId'):
            added_notification_to_db = NotificationSaveInDB(**notification.dict(), sender_id = sender_id)
            created_at = datetime.utcnow()
            row = await db.client[DATABASE_NAME][notifications_collection_name].insert_one(
            dict(added_notification_to_db.dict(), created_at=created_at, updated_at=created_at)
            )
            if row.inserted_id: return True
        return False
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def send_notifications_with_tags(notification: Notification, sender_id: ObjectId) -> bool:
    try:
        title = notification.title
        msg = notification.description
        gcm_msg_json = json.dumps({
            'notification': {
                "title": title, 
                "body": msg,
                "icon": notification.icon_url
            }
        })

        msg_to_be_sent = {
            'default': msg,
            'GCM': gcm_msg_json
        }
        # Target Arn: Getting device endpoint for the reciever.
        if notification.sent_tags:
            sns_client = await get_sns_client()
            for tag in notification.sent_tags:
                from visitegypt.infra.database.repositories.tag_repository import get_all_users_of_tags
                users_of_tag = await get_all_users_of_tags(tag_ids=[tag])
                print(users_of_tag)
                for user in users_of_tag:            
                    res = sns_client.publish(TargetArn=user.device_arn_endpoint, Message=json.dumps(msg_to_be_sent), MessageStructure='json')
                    print(res)
            added_notification_to_db = NotificationSaveInDB(**notification.dict(), sender_id = sender_id)
            row = await db.client[DATABASE_NAME][notifications_collection_name].insert_one(
            added_notification_to_db.dict()
            )
            if row.inserted_id: return True
        return False
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def send_notification_to_specific_users(notification: Notification, sender_id: ObjectId) -> bool:
    try:
        title = notification.title
        msg = notification.description
        gcm_msg_json = json.dumps({
            'notification': {
                "title": title, 
                "body": msg,
                "icon": notification.icon_url
            }
        })

        msg_to_be_sent = {
            'default': msg,
            'GCM': gcm_msg_json
        }
        # Target Arn: Getting device endpoint for the reciever.
        if len(notification.sent_users_ids) == 1:
            # Get device endpoint for a user with id
            from visitegypt.infra.database.repositories.user_repository import get_device_endpoint
            user_endpoint = (await get_device_endpoint(notification.sent_users_ids[0])).device_arn_endpoint
            
            sns_client = await get_sns_client()
            res = sns_client.publish(TargetArn=user_endpoint, Message=json.dumps(msg_to_be_sent), MessageStructure='json')
            if res.get('MessageId'):
                added_notification_to_db = NotificationSaveInDB(**notification.dict(), sender_id = sender_id)
                row = await db.client[DATABASE_NAME][notifications_collection_name].insert_one(
                added_notification_to_db.dict()
                )
                if row.inserted_id: return True
        return False
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_filtered_notifications(
    page_num: int, limit: int, filters: Dict
) -> NotificationsPageResponse:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][notifications_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        notifications_list = await cursor.to_list(limit+1)
        
        has_next = len(notifications_list) > limit
        if len(notifications_list) > 1: del notifications_list[-1]
        if not notifications_list:
            raise NotificationNotFoundError
        document_count = await db.client[DATABASE_NAME][notifications_collection_name].count_documents(filters)
        notifications_list_response = [NotificationSaveInDB.from_mongo(place) for place in notifications_list]
        return NotificationsPageResponse(
            current_page=page_num, has_next=has_next, notifications=notifications_list_response, content_range=document_count
        )
    except NotificationNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)