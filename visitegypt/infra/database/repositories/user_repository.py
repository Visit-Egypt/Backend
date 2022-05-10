from typing import List, Optional
from pydantic import EmailStr
import pymongo
from visitegypt.core.accounts.entities.user import (
    UserResponse,
    UserUpdate,
    UserUpdatePassword,
    User,
    UsersPageResponse,
    Badge,
    BadgeTask,
    BadgeUpdate,
    BadgeResponse,
    PlaceActivityUpdate,
    RequestTripMate,
    RequestTripMateInDB,
    UserResponseInTags,
    UserPushNotification
)
from visitegypt.core.utilities.entities.notification import Notification
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import (
    users_collection_name,
    calculate_start_index,
    check_has_next,
    badges_collection_name,
    check_next
)
from visitegypt.core.errors.user_errors import (
    UserNotFoundError,
    UserIsFollower,
    TripRequestNotFound,
    UserIsNotFollowed,
    PlaceIsAlreadyInFavs,
    PlaceIsNotInFavs
)
from visitegypt.core.errors.tag_error import TagsNotFound
from bson import ObjectId
from pymongo import ReturnDocument
from visitegypt.infra.errors import InfrastructureException
from visitegypt.infra.database.repositories.tag_repository import (
    update_many_tag_users,
    remove_many_tag_users
)

from loguru import logger
from fastapi import HTTPException, status
async def create_user(new_user: User) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].insert_one(
            new_user.dict()
        )
        if row.inserted_id:
            return await get_user_by_id(row.inserted_id)
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user(updated_user: UserUpdate, user_id: str) -> Optional[UserResponse]:
    try:
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": {k: v for k, v in updated_user.dict().items() if v}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            return UserResponse.from_mongo(result)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user_password(updated_user: UserUpdatePassword, user_id: str) -> Optional[UserResponse]:
    try:
        if updated_user:
            result = await db.client[DATABASE_NAME][
                users_collection_name
            ].find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"hashed_password": str(updated_user.hashed_password)}},
                return_document=ReturnDocument.AFTER,
            )
        if result:
            return UserResponse.from_mongo(result)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_user_role(updated_user: str, user_id: str) -> Optional[UserResponse]:
    try:
        if updated_user:
            result = await db.client[DATABASE_NAME][
                users_collection_name
            ].find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"user_role": updated_user}},
                return_document=ReturnDocument.AFTER,
            )
        if result:
            return UserResponse.from_mongo(result)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def delete_user(user_id: str) -> Optional[bool]:
    try:
        res = await db.client[DATABASE_NAME][users_collection_name].delete_one(
            {"_id": ObjectId(user_id)}
        )
        if res.deleted_count == 1:
            return True
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": ObjectId(user_id)}
        )
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_user_by_email(user_email: EmailStr) -> Optional[UserResponse]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"email": user_email}
        )
        if row:
            return UserResponse.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except pymongo.errors.OperationFailure as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.details)
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_user_hashed_password(user_id: str) -> str:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": ObjectId(user_id)}
        )
        if row:
            return row["hashed_password"]
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_all_users(page_num: int, limit: int) -> List[UsersPageResponse]:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][users_collection_name]
            .find()
            .skip(start_index)
            .limit(limit)
        )
        users_list = await cursor.to_list(limit)
        if len(users_list) <= 0:
            raise UserNotFoundError
        users_list_response = [UserResponse.from_mongo(user) for user in users_list]
        has_next = check_next(limit,users_list_response)
        return UsersPageResponse(
            current_page=page_num, has_next=has_next, users=users_list_response
        )
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)



async def update_user_tokenID(user_id: str,new_toke_id:str,old_token_id:str=None):
    try:
        if  old_token_id != None:
            await check_user_token(user_id=user_id,token_id=old_token_id)
        await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": new_toke_id}})
    except Exception as e:
        raise e

async def check_user_token(user_id: str,token_id:str) -> UserResponse:
    security_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token ID is please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one(
                {"_id": ObjectId(user_id)}
            )
        
        if  token_id != None and str(user["tokenID"]) !=  token_id:
                await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": "Loged Out"}})
                raise security_exception
        return UserResponse.from_mongo(user)
    except Exception as e:
        raise e

async def user_logout(user_id: str):
    try:
        await db.client[DATABASE_NAME][users_collection_name].update_one({"_id": ObjectId(user_id)}, {'$set': {"tokenID": "Loged Out"}})
    except Exception as e:
        raise e

async def update_badge_task(user_id:str, new_task:BadgeTask):
    try:
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            { "_id": user_id, "badge_tasks.badge_id": new_task.badge_id, "badge_tasks.taskTitle": new_task.taskTitle },
            { "$set": { "badge_tasks.$.progress": new_task.progress} },
            return_document=ReturnDocument.AFTER,
        )
        if result != None:
            return result["badge_tasks"]
        else:
            if(await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id": user_id, "badges.id": new_task.badge_id}) == None):
                new_badge = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update({ "_id": user_id },
                { "$addToSet": {"badges":Badge(id=new_task.badge_id).dict() }},
                return_document=ReturnDocument.AFTER,)

            new = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$push": {"badge_tasks": new_task.dict()}},
            return_document=ReturnDocument.AFTER,)
            if new:
                return new["badge_tasks"]
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def update_badge(user_id: str ,badge_id: str,new_badge: BadgeUpdate):
    try:
        user = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one({ "_id":ObjectId(user_id)})
        badge = next((item for item in user["badges"] if item["id"] == badge_id), None)
        for k,v in new_badge:
            if(v != None):
                badge[k] = v
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            { "_id": user_id, "badges.id": badge_id},
            {"$set": {"badges.$":badge}},
            return_document=ReturnDocument.AFTER,
        )
        return result["badges"]
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_badges( user_id: str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badges = user["badges"]
        tasks = user["badge_tasks"]
        res = []
        for i in badges:
            badge_tasks = [item for item in tasks if item["badge_id"] == i["id"]]
            badge = BadgeResponse(
                id = i["id"],
                progress = i["progress"],
                pinned = i["pinned"],
                owned = i["owned"],
                badge_tasks = badge_tasks
            )
            res.append(badge)

        return res
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def update_user_activity(user_id:str,activity_id:str,new_activity:PlaceActivityUpdate):
    try:
        user = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one({ "_id":ObjectId(user_id)})
        activity = next((item for item in user["placeActivities"] if item["id"] == activity_id), None)
        if(not activity):
            new_ac ={
            "id":activity_id,
            "finished":new_activity.finished,
            "progress":new_activity.progress
            }
            new = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$push": {"placeActivities": new_ac}},
                return_document=ReturnDocument.AFTER,)
            return new["placeActivities"]

        for k,v in new_activity:
            if(v != None):
                activity[k] = v
        result = await db.client[DATABASE_NAME][
            users_collection_name
        ].find_one_and_update(
            { "_id": user_id, "placeActivities.id": activity_id},
            {"$set": {"placeActivities.$":activity}},
            return_document=ReturnDocument.AFTER,
        )
        return result["placeActivities"]
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_activities( user_id: str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        activities = user["placeActivities"]
        return activities
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e


async def follow_user(current_user: UserResponse, user_id: str) -> bool:
    try:
        user_to_follow = await get_user_by_id(user_id)
        if user_to_follow is None: raise UserNotFoundError
        # if user_to_follow.followers is not None:
        ch = [n for n in  user_to_follow.followers if n == current_user.id]
        if ch: raise UserIsFollower
        # In this phase user1 is not followed by current user
        # We need to save current user in user1 followers and save user1 in current user following
        # We are going to use the id not the full user

        user_to_follow.followers.append(current_user.id)
        current_user.following.append(user_to_follow.id)

        await update_user(UserUpdate(followers=user_to_follow.followers), user_id=user_id)
        await update_user(UserUpdate(following=current_user.following), user_id=str(current_user.id))

        # Send Notification to the followed user (user_to_follow)
        from visitegypt.infra.database.repositories import notification_repository
        notification = Notification(title=f'A new follower', description=f'{current_user.first_name} {current_user.last_name} has followed you.', sent_users_ids=[user_to_follow.id])
        await notification_repository.send_notification_to_specific_users(notification, current_user.id)
        return True
    except UserIsFollower as usf: raise usf
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def unfollow_user(current_user: UserResponse, user_id: str) -> bool:
    try:
        user_to_unfollow = await get_user_by_id(user_id)
        if user_to_unfollow is None: raise UserNotFoundError
        ch = [n for n in  user_to_unfollow.followers if n == current_user.id]
        if not ch: raise UserIsNotFollowed
        # In this phase user1 is followed by current user
        # We need to remove current user in user1 followers and remove user1 in current user following
        # We are going to use the id not the full user

        user_to_unfollow.followers.remove(current_user.id)
        current_user.following.remove(user_to_unfollow.id)

        await update_user(UserUpdate(followers=user_to_unfollow.followers), user_id=user_id)
        await update_user(UserUpdate(following=current_user.following), user_id=str(current_user.id))

        return True
    except UserIsNotFollowed as uu: raise uu
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def request_trip_mate(current_user: UserResponse, user_id: str, request_mate: RequestTripMate)  -> Optional[UserResponse]:
    try:
        request_trip_mate = RequestTripMateInDB(**request_mate.dict(), is_approved=False, initator_id=current_user.id, id=ObjectId())
        user_req = await get_user_by_id(user_id)
        if user_req.trip_mate_requests is None:
            user_req.trip_mate_requests = []
        user_req.trip_mate_requests.append(request_trip_mate.dict())
        updated_user = await update_user(UserUpdate(trip_mate_requests=user_req.trip_mate_requests), user_id)
        if updated_user:
            return updated_user
    except UserNotFoundError as un: raise un
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def approve_request_trip_mate(current_user: UserResponse, req_id: str) -> Optional[UserResponse]:
    try:
        req_found = False
        for req in current_user.trip_mate_requests:
            if req.id == ObjectId(req_id):
                req.is_approved = True
                req_found = True
                break
        if not req_found: raise TripRequestNotFound
        updated_user = await update_user(UserUpdate(trip_mate_requests=current_user.trip_mate_requests), current_user.id)
        if updated_user:
            return updated_user
    except UserNotFoundError as un: raise un
    except TripRequestNotFound as trf: raise trf
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def add_preferences(current_user: UserResponse, list_of_prefs: List[str]) -> Optional[UserResponse]:
    # 1- Check if the tag is already in Tags collection
    # 2- Check if the user has the tag already
    # 3- Add the tag to user's interests list and add the user id to tag's user list
    # Put tag id in user
    try:
        user_prefs_set = set(current_user.interests)
        new_prefs = set([ObjectId(pref) for pref in list_of_prefs])
        prefs_to_add = new_prefs.difference(user_prefs_set)
        updated_user = await update_user(UserUpdate(interests=list(prefs_to_add)+current_user.interests), current_user.id)
        updated_tag = await update_many_tag_users(str(current_user.id), list(prefs_to_add))
        if updated_tag: return updated_user
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def remove_preferences(current_user: UserResponse, list_of_remv_prefs: List[str]) -> Optional[UserResponse]:
    try:
        prefs_object_ids = [ObjectId(pref) for pref in list_of_remv_prefs]

        # Remove them from users' interests list:
        result = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": ObjectId(str(current_user.id))},
            {"$pull": {"interests": { '$in': prefs_object_ids}}},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            # Remove user if from tags collections
            updated_tag = await remove_many_tag_users(str(current_user.id), prefs_object_ids)
            if updated_tag: return UserResponse.from_mongo(result)
        
    except UserNotFoundError as ue:
        raise ue
    except TagsNotFound as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def get_bulk_users_by_id(users_ids: List[ObjectId]) -> Optional[List[UserResponseInTags]]:
    try:
        cursor = (
            db.client[DATABASE_NAME][users_collection_name]
            .find({'_id': {'$in': users_ids}})
        )
        users_list = await cursor.to_list(length=None)
        if len(users_list) <= 0:
            raise UserNotFoundError
        return [UserResponseInTags.from_mongo(user) for user in users_list]
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def add_place_to_favs(current_user: UserResponse, place_id: str) -> Optional[bool]:
    try:
        current_user_favs = current_user.fav_places
        o_place_id = ObjectId(place_id)
        # Check if place id is already in the list
        ch = [n for n in  current_user_favs if n == o_place_id]
        if ch: raise PlaceIsAlreadyInFavs

        current_user_favs.append(o_place_id)
        result = await update_user(UserUpdate(fav_places=current_user_favs), user_id=str(current_user.id)) 

        if result: return True
        else: return False

    except PlaceIsAlreadyInFavs as pia: raise pia
    except UserNotFoundError as ue: raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def remove_place_from_favs(current_user: UserResponse, place_id: str) -> Optional[bool]:
    try:
        current_user_favs = current_user.fav_places
        o_place_id = ObjectId(place_id)
        # Check if place id is not in the list
        ch = [n for n in  current_user_favs if n == o_place_id]
        if not ch: raise PlaceIsNotInFavs
        current_user_favs.remove(o_place_id)
        result = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": ObjectId(str(current_user.id))},
            {"$pull": {"fav_places": o_place_id}},
            return_document=ReturnDocument.AFTER,
        )
        if result: return True
        else: return False

    except PlaceIsNotInFavs as pia: raise pia
    except UserNotFoundError as ue: raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)


async def get_device_endpoint(user_id: ObjectId) -> Optional[UserPushNotification]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": user_id}
        )
        if row:
            return UserPushNotification.from_mongo(row)
        raise UserNotFoundError
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)