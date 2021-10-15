from fastapi import APIRouter, status, HTTPException, Security
from loguru import logger
from visitegypt.api.container import get_dependencies
from visitegypt.core.places.services import place_service
from visitegypt.core.places.entities.place import PlacesPageResponse,PlaceInDB, CreatePlace, UpdatePlace, review, PlaceBase
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.api.routers.account.util import common_parameters, get_current_user
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.place_error import *
from visitegypt.core.accounts.entities.roles import *

repo = get_dependencies().place_repo

router = APIRouter(tags=['Place'])


@router.get(
    "/",
    response_model=PlacesPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all places"
)
async def get_places(page_num : int = 1, limit : int = 15):
    try:
        return await place_service.get_all_places_paged(repo, page_num=page_num, limit=limit)
    except Exception as e:
        if isinstance(e, PlaceNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Places"))
        else: raise e

@router.get(
    "/{place_id}",
    response_model=PlaceInDB,
    status_code=status.HTTP_200_OK,
    summary="Get Place"
)
async def get_place_by_id(place_id):
    try:
        return await place_service.get_place_by_id(repo, place_id)
    except Exception as e:
        if isinstance(e, PlaceNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Place"))
        else: raise e

@router.post("/", response_model=PlaceInDB, status_code=status.HTTP_201_CREATED, summary="Add new Place")
async def add_new_place(new_place: PlaceBase, current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    )):
    try:
        return await place_service.create_place(repo, new_place)
    except PlaceAlreadyExists: raise HTTPException(409, detail="Place Already exists")
    except Exception as e:
        raise e

@router.put("/{place_id}", response_model=PlaceInDB, status_code=status.HTTP_200_OK, summary="Update a Place")
async def update_place(place_id: str,place_to_update: UpdatePlace, current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    )):
    try:
        return await place_service.update_place(repo, place_to_update, place_id)
    except Exception as e:
        if isinstance(e, PlaceNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Place"))
        else: raise HTTPException(422, detail=str(e))

@router.delete("/{place_id}", status_code=status.HTTP_200_OK, summary="Delete a Place")
async def delete_place(place_id: str, current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    )):
    try:
        return await place_service.delete_place(repo, place_id)
    except Exception as e:
        if isinstance(e, PlaceNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Place"))
        else: raise HTTPException(422, detail=str(e))

@router.post("/review/{place_id}", status_code=status.HTTP_201_CREATED, summary="Add new review to a place")
async def add_new_review(place_id,new_review: review, current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"],Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    )):
    if str(new_review.user_id) == str(current_user.id) or current_user.user_role == Role.ADMIN["name"] or current_user.user_role == Role.SUPER_ADMIN["name"]:
        try:
            return await place_service.add_review(repo, place_id, new_review)
        except Exception as e:
            raise e
    else:
        raise HTTPException(401, detail="Unautherized")

@router.delete("/review/{place_id}", status_code=status.HTTP_200_OK, summary="Delete review from a place")
async def delete_review(review:review, place_id: str, current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"],Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    )):
    if str(review.user_id) == str(current_user.id) or current_user.user_role == Role.ADMIN["name"] or current_user.user_role == Role.SUPER_ADMIN["name"]:
        try:
            return await place_service.delete_review(repo, place_id,review)
        except Exception as e:
            if isinstance(e, PlaceNotFoundError): raise HTTPException(404, detail=MESSAGE_404("Place"))
            else: raise HTTPException(422, detail=str(e))
    else:
        raise HTTPException(401, detail="Unautherized")