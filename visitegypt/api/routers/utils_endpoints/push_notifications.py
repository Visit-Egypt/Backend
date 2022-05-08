from email import message
from fastapi import APIRouter, status, HTTPException, Security
from visitegypt.api.container import get_dependencies
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.utils import get_current_user
from visitegypt.core.accounts.entities.user import (UserResponse)
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.core.utilities.entities.notification import RegisterDeviceTokenRequest, RegisterDeviceTokenResponse, NotificationSentResponse, Notification
from visitegypt.core.utilities.services import notification_service
router = APIRouter(responses=generate_response_for_openapi("Push Notifcation"))

repo = get_dependencies().notification_repo

@router.post('/register-device',
    response_model= RegisterDeviceTokenResponse,
    status_code=status.HTTP_201_CREATED, 
    summary='Register Device to the notification', 
    tags=["Push Notifications"])
async def register_token(token: RegisterDeviceTokenRequest, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        result = await notification_service.register_new_device(repo, str(current_user.id), token.device_token)
        if result: return RegisterDeviceTokenResponse(message="User's device has been registered")
        else: return RegisterDeviceTokenResponse(message="User's device has not been registered")
    except Exception as e: raise e


@router.post('/send',
    response_model= NotificationSentResponse,
    status_code=status.HTTP_201_CREATED, 
    summary='Send notification', 
    tags=["Push Notifications"])
async def send_notification(notification: Notification, current_user: UserResponse = Security( get_current_user,scopes=[Role.USER["name"], Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        result = await notification_service.send_notification(repo, notification, current_user.id)
        if result: return NotificationSentResponse(message='Notification has been sent')
        else: return NotificationSentResponse(message='Error in sending the notification')
    except Exception as e: raise e

