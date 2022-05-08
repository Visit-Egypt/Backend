from visitegypt.core.utilities.protocols.notification_repo import NotificationRepo
from visitegypt.core.utilities.entities.notification import Notification
from bson import ObjectId

async def register_new_device(repo: NotificationRepo, user_id: str, device_token: str) -> bool:
    try:
        return await repo.register_device_token(user_id, device_token)
    except Exception as e: raise e


async def send_notification(repo: NotificationRepo, notification: Notification, sender_id: ObjectId) -> bool:
    """
        sent_tags: Optional[List[GetTagResponse]] = []
        sent_users_ids: Optional[List[OID]] = []
    """
    try:
        if  notification.sent_tags:
            # Sending the notification using tags ids.
            return await repo.send_notifications_with_tags(notification, sender_id)
        elif  notification.sent_users_ids:
            return await repo.send_notification_to_specific_users(notification, sender_id)
        else: return await repo.send_notification(notification, sender_id)
        
    except Exception as e: raise e