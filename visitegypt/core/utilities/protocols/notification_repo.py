from typing import Protocol
from bson import ObjectId
from visitegypt.core.utilities.entities.notification import Notification, NotificationSentResponse

class NotificationRepo(Protocol):
    async def register_device_token(self, user_id: str, device_token: str) -> bool:
        pass

    async def send_notification(self, notification: Notification, sender_id: ObjectId) -> bool:
        pass

    
    async def send_notifications_with_tags(self, notification: Notification, sender_id: ObjectId) -> bool:
        pass

    async def send_notification_to_specific_users(self, notification: Notification, sender_id: ObjectId) -> bool:
        pass