from typing import List, Optional, Dict
from pydantic import EmailStr
import pymongo
from visitegypt.core.errors.place_error import PlaceNotFoundError
from visitegypt.core.accounts.entities.user import (
    UserResponse,
    UserUpdate,
    UserAR,
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
    UserPushNotification,
    UserFollowResp,
    BadgeResponseDetail
)
from visitegypt.core.badges.entities.badge import BadgeInDB
from visitegypt.core.utilities.entities.notification import Notification
from visitegypt.infra.database.events import db
from visitegypt.config.environment import DATABASE_NAME
from visitegypt.infra.database.utils import (
    users_collection_name,
    badges_collection_name,
    places_collection_name,
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
from visitegypt.infra.database.repositories.place_repository import get_some_places,get_place_by_explore
from loguru import logger
from fastapi import HTTPException, status
SOCIAL_BUTTERFLY_ID = "62b71137ff1abae844f3ed60"

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

async def get_user_ar(user_id: str) -> Optional[UserAR]:
    try:
        row = await db.client[DATABASE_NAME][users_collection_name].find_one(
            {"_id": ObjectId(user_id)}
        )
        if row:
            return UserAR(**row)
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


async def get_all_users(page_num: int = 1, limit: int = 15, filters: Dict = None) -> List[UsersPageResponse]:
    try:
        indcies = calculate_start_index(limit, page_num)
        start_index: int = indcies[0]
        cursor = (
            db.client[DATABASE_NAME][users_collection_name]
            .find(filters)
            .skip(start_index)
            .limit(limit+1)
        )
        users_list = await cursor.to_list(limit+1)
        document_count = await db.client[DATABASE_NAME][users_collection_name].count_documents(filters)
        if not users_list:
            raise UserNotFoundError
        users_list_response = [UserResponse.from_mongo(user) for user in users_list]
        has_next = len(users_list) > limit
        return UsersPageResponse(
            current_page=page_num, has_next=has_next, users=users_list_response, content_range=document_count
        )
    except UserNotFoundError as uae: raise uae
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

async def get_user_badges_detail( user_id: str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badges = user["badges"]
        tasks = user["badge_tasks"]
        res = []
        for i in badges:
            badge_tasks = [item for item in tasks if item["badge_id"] == i["id"]]
            badgedetail = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "_id":ObjectId(i["id"])}))
            badge = {
                "badge": badgedetail,
                "progress":i["progress"],
                "pinned":i["pinned"],
                "owned":i["owned"],
                "badge_tasks":badge_tasks
            }
            res.append(badge)

        return res
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def claim_location(user_id:str, city:str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({"title":"King of "+city.capitalize()}))
        badgeTask = badge.badge_tasks[0]
        #badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        badgeTaskFromUser = next((item for item in user["badge_tasks"] if item['taskTitle'] == badgeTask.taskTitle and item['badge_id'] == str(badge.id)), None)
        if(badgeTaskFromUser):
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle=badgeTask.taskTitle,progress=badgeTaskFromUser["progress"]+1))
        else:
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle=badgeTask.taskTitle,progress=1))
            user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+badge.xp),user_id)
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def visit_place(user_id: str ,place_id:str):
    try:
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        visitActivity = next((item for item in place["placeActivities"] if item['type'] == 0), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "place_id":place_id}))
        await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(finished="true",progress=1))
        await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="visit the place",progress=1))
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]),user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def update_social_badge(user_id:str, type:str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({"_id":ObjectId(SOCIAL_BUTTERFLY_ID)}))
        if(type == "review"):
            badgeTask = next((item for item in badge.badge_tasks if item.taskTitle == "review 10 places"), None)
        elif(type == "post"):
            badgeTask = next((item for item in badge.badge_tasks if item.taskTitle == "post 3 posts"), None)
        else:
            raise "Wrong Type"
        badgeTaskFromUser = next((item for item in user["badge_tasks"] if item['taskTitle'] == badgeTask.taskTitle and item['badge_id'] == str(badge.id)), None)
        if(badgeTaskFromUser):
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle=badgeTask.taskTitle,progress=badgeTaskFromUser["progress"]+1))
            if(badgeTaskFromUser["progress"] >= badgeTask.max_progress):
                return
        else:
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle=badgeTask.taskTitle,progress=1))
            user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
                await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
                await update_user(UserUpdate(xp=user["xp"]+badge.xp),user_id)
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def review_place(user_id: str ,place_id:str):
    try:
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        visitActivity = next((item for item in place["placeActivities"] if item['type'] == 4), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({"place_id":place_id}))
        await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(finished="true",progress=1))
        await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="review the place",progress=1))
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]),user_id)
        await update_social_badge(user_id,"review")
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def add_post(user_id: str ,place_id:str):
    try:
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        visitActivity = next((item for item in place["placeActivities"] if item['type'] == 1), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "place_id":place_id}))
        await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(finished="true",progress=1))
        await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="post a post",progress=1))
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]),user_id)
        await update_social_badge(user_id,"post")
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def chatbot_artifact(user_id: str ,place_id:str):
    try: 
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        visitActivity = next((item for item in place["placeActivities"] if item['type'] == 2), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "place_id":place_id}))
        await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(finished="true",progress=1))
        await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="ask Anubis about the artifacts",progress=1))
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]),user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def chatbot_place(user_id: str ,place_id:str):
    try:
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        visitActivity = next((item for item in place["placeActivities"] if item['type'] == 3), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "place_id":place_id}))
        await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(finished="true",progress=1))
        await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="ask Anubis about the place",progress=1))
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+visitActivity["xp"]),user_id)
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def scan_object(user_id: str ,place_id:str,explore_id:str):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        place = await db.client[DATABASE_NAME][places_collection_name].find_one({ "_id":ObjectId(place_id)})
        #visitActivity = next((item for item in place["placeActivities"] if item['title'] == "AR"), None)
        explore = next((item for item in place["explores"] if item['id'] == explore_id), None)
        badge = BadgeInDB.from_mongo(await db.client[DATABASE_NAME][badges_collection_name].find_one({ "place_id":place_id}))
        badgeTask = next((item for item in badge.badge_tasks if item.taskTitle == "explore the artifacts"), None)
        #badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        #activityFromUser = next((item for item in user["placeActivities"] if item['id'] == visitActivity["id"]), None)
        badgeTaskFromUser = next((item for item in user["badge_tasks"] if item['taskTitle'] == badgeTask.taskTitle and item['badge_id'] == str(badge.id)), None)
        await update_user_activity(user_id,explore_id,PlaceActivityUpdate(finished="true",progress=1))
        # if(activityFromUser["progress"] == visitActivity["maxProgress"]-1):
        #     await update_user_activity(user_id,explore_id,PlaceActivityUpdate(finished="true",progress=1))
        # else:
        #     await update_user_activity(user_id,visitActivity["id"],PlaceActivityUpdate(progress=activityFromUser["progress"]+1))
        if(badgeTaskFromUser):
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="explore the artifacts",progress=badgeTaskFromUser["progress"]+1))
        else:
            await update_badge_task(user_id,BadgeTask(badge_id=str(badge.id),taskTitle="explore the artifacts",progress=1))
            user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        badgeFromUser = next((item for item in user["badges"] if item['id'] == str(badge.id)), None)
        if(badgeFromUser["progress"] == badge.max_progress-1):
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1,owned="true"))
            await update_user(UserUpdate(xp=user["xp"]+explore["xp"]+badge.xp),user_id)
            await claim_location(user_id,place["city"])
        else:
            await update_badge(user_id,str(badge.id),BadgeUpdate(progress=badgeFromUser["progress"]+1))
            await update_user(UserUpdate(xp=user["xp"]+explore["xp"]),user_id)
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

async def get_user_activities_detail(user_id: str,place_id:str=None):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        activities = user["placeActivities"]
        finalActivities = []
        for i in activities:
            activityid = i["id"]
            try:
                place = await get_some_places([activityid])
                if(place_id and place_id != str(place[0].id)):
                    continue
                placeActivities=place[0].placeActivities
                for r in placeActivities:
                    if r.id == activityid:
                        activity = r.dict()
                i["activity"] = activity
                finalActivities.append(i)
            except PlaceNotFoundError:
                place = await get_place_by_explore([activityid])
                if(place_id and place_id != str(place[0].id)):
                    continue
                placeActivities=place[0].explores
                for r in placeActivities:
                    if r.id == activityid:
                        activity = r.dict()
                i["activity"] = activity
                finalActivities.append(i)
            except Exception as e:
                raise e
            
        return finalActivities
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_only_activities_detail(user_id: str,place_id:str=None):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        activities = user["placeActivities"]
        onlyActivities = []
        for i in activities:
            activityid = i["id"]
            try:
                place = await get_some_places([activityid])
                if(place_id and place_id != str(place[0].id)):
                    continue
                placeActivities=place[0].placeActivities
                for r in placeActivities:
                    if r.id == activityid:
                        activity = r.dict()
                i["activity"] = activity
                onlyActivities.append(i)
            except PlaceNotFoundError:
                continue
            except Exception as e:
                raise e
        return onlyActivities
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def get_user_only_explore_detail(user_id: str,place_id:str=None):
    try:
        user = await db.client[DATABASE_NAME][users_collection_name].find_one({ "_id":ObjectId(user_id)})
        activities = user["placeActivities"]
        onlyExplores = []
        for i in activities:
            activityid = i["id"]
            try:
                place = await get_place_by_explore([activityid])
                if(place_id and place_id != str(place[0].id)):
                    continue
                placeActivities=place[0].explores
                for r in placeActivities:
                    if r.id == activityid:
                        activity = r.dict()
                i["activity"] = activity
                onlyExplores.append(i)
            except PlaceNotFoundError:
                continue
            except Exception as e:
                raise e
        return onlyExplores
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def follow_user(current_user: UserResponse, user_id: str) -> UserFollowResp:
    try:
        user_to_follow = await get_user_by_id(user_id)
        if user_to_follow is None: raise UserNotFoundError
        # if user_to_follow.followers is not None:
        ch = [n for n in  user_to_follow.followers if n == current_user.id]
        if ch: raise UserIsFollower
        # In this phase user1 is not followed by current user
        # We need to save current user in user1 followers and save user1 in current user following
        # We are going to use the id not the full user

        # Push User ID to each user document corresponding list

        updated_user_to_follow = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": user_to_follow.id},
            {"$push": {"followers": current_user.id}},
            return_document=ReturnDocument.AFTER,
        )
        updated_current_user = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": current_user.id},
            {"$push": {"following": user_to_follow.id}},
            return_document=ReturnDocument.AFTER,
        )
        #user_to_follow.followers.append(current_user.id)
        #current_user.following.append(user_to_follow.id)

        #updated_user_to_follow = await update_user(UserUpdate(followers=user_to_follow.followers), user_id=user_id)
        #await update_user(UserUpdate(following=current_user.following), user_id=str(current_user.id))

        """
        # Send Notification to the followed user (user_to_follow)
        from visitegypt.infra.database.repositories import notification_repository
        notification = Notification(title=f'A new follower', description=f'{current_user.first_name} {current_user.last_name} has followed you.', sent_users_ids=[user_to_follow.id])
        await notification_repository.send_notification_to_specific_users(notification, current_user.id)
        """        
        return UserFollowResp(followers_num = str(len(updated_user_to_follow.get('followers'))))
    except UserIsFollower as usf: raise usf
    except UserNotFoundError as ue:
        raise ue
    except Exception as e:
        logger.exception(e.__cause__)
        raise InfrastructureException(e.__repr__)

async def unfollow_user(current_user: UserResponse, user_id: str) -> UserFollowResp:
    try:
        user_to_unfollow = await get_user_by_id(user_id)
        
        if user_to_unfollow is None: raise UserNotFoundError
        ch = [n for n in  user_to_unfollow.followers if n == current_user.id]
        if not ch: raise UserIsNotFollowed
        # In this phase user1 is followed by current user
        # We need to remove current user in user1 followers and remove user1 in current user following
        # We are going to use the id not the full user

        # Pull User ID to each user document corresponding list

        updated_user_to_unfollow = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": user_to_unfollow.id},
            {"$pull": {"followers": current_user.id}},
            return_document=ReturnDocument.AFTER,
        )
        updated_current_user = await db.client[DATABASE_NAME][users_collection_name].find_one_and_update(
            {"_id": current_user.id},
            {"$pull": {"following": user_to_unfollow.id}},
            return_document=ReturnDocument.AFTER,
        )
        #user_to_unfollow.followers.remove(current_user.id)
        #current_user.following.remove(user_to_unfollow.id)

        #updated_user_to_unfollow =await update_user(UserUpdate(followers=user_to_unfollow.followers), user_id=user_id)
        #await update_user(UserUpdate(following=current_user.following), user_id=str(current_user.id))

        return UserFollowResp(followers_num = str(len(updated_user_to_unfollow.get('followers'))))
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
