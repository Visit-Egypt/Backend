from fastapi import APIRouter, status, HTTPException, Security, BackgroundTasks, Depends
from typing import Dict
from visitegypt.api.container import get_dependencies
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
from visitegypt.api.utils import get_current_user, common_parameters
from visitegypt.core.accounts.entities.user import (UserResponse)
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.core.utilities.entities.notification import RegisterDeviceTokenRequest, RegisterDeviceTokenResponse, NotificationSentResponse, Notification, NotificationsPageResponse
from visitegypt.core.utilities.services import notification_service
from visitegypt.core.errors.notifications_error import NotificationNotFoundError
from visitegypt.resources.strings import MESSAGE_404

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
async def send_notification(notification: Notification, background_tasks: BackgroundTasks, current_user: UserResponse = Security( get_current_user,scopes=[Role.ADMIN["name"], Role.SUPER_ADMIN["name"]])):
    try:
        background_tasks.add_task(notification_service.send_notification, repo, notification, current_user.id)
        # result = await notification_service.send_notification(repo, notification, current_user.id)
        # if result: return NotificationSentResponse(message='Notification has been sent')
        # else: return NotificationSentResponse(message='Error in sending the notification')
        return {'message': 'Notification is being sent in the background'}
    except Exception as e: raise e

@router.get(
    "/",
    response_model=NotificationsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all notifications",
    tags=["Push Notifications"]
)
async def get_notifications(params: Dict = Depends(common_parameters)):
    try:
        if params["page_num"] < 1 or params["limit"] < 1:
            raise HTTPException(422, "Query Params shouldn't be less than 1")
        return await notification_service.get_filtered_notifications(
            repo,
            page_num=params["page_num"],
            limit=params["limit"],
            filters=params["filters"],
        )
    except NotificationNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Notifications"))
    except Exception as e: raise e
