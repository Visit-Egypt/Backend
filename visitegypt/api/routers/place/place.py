import json
from fastapi import APIRouter, status, HTTPException, Security, WebSocket
from visitegypt.api.container import get_dependencies
from visitegypt.core.places.services import place_service
from visitegypt.core.places.entities.place import (
    PlacesPageResponse,
    PlaceInDB,
    UpdatePlace,
    review,
    PlaceBase,
    PlacesForSearchList,
    PlaceForSearch
)
from visitegypt.core.accounts.entities.user import UserResponse
from visitegypt.api.utils import get_current_user
from visitegypt.resources.strings import MESSAGE_404
from visitegypt.core.errors.place_error import PlaceNotFoundError, PlaceAlreadyExists
from visitegypt.core.accounts.entities.roles import Role
from visitegypt.api.errors.generate_http_response_openapi import generate_response_for_openapi
repo = get_dependencies().place_repo

router = APIRouter(responses=generate_response_for_openapi("Place"))


@router.get(
    "/",
    response_model=PlacesPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all places",
    tags=["Place"]
)
async def get_places(page_num: int = 1, limit: int = 15):
    try:
        return await place_service.get_all_places_paged(
            repo, page_num=page_num, limit=limit
        )
    except PlaceNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Places"))
    except Exception as e: raise e

@router.get(
    "/title",
    response_model=PlaceInDB,
    status_code=status.HTTP_200_OK,
    summary="Get Place By Title",
    tags=["Place"]
)
async def get_place_by_title(place_title: str):
    try:
        return await place_service.get_place_by_title(repo, place_title)
    except PlaceNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Place"))
    except Exception as e: raise e

@router.get(
    "/{place_id}",
    response_model=PlaceInDB,
    status_code=status.HTTP_200_OK,
    summary="Get Place",
    tags=["Place"]
)
async def get_place_by_id(place_id: str):
    try:
        return await place_service.get_place_by_id(repo, place_id)
    except PlaceNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Place"))
    except Exception as e: raise e





@router.post(
    "/",
    response_model=PlaceInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Add new Place",
    tags=["Admin Panel"]
)
async def add_new_place(
    new_place: PlaceBase,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await place_service.create_place(repo, new_place)
    except PlaceAlreadyExists:
        raise HTTPException(409, detail="Place Already exists")
    except Exception as e:
        raise e


@router.put(
    "/{place_id}",
    response_model=PlaceInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Update a Place",
    tags=["Admin Panel"]
)
async def update_place(
    place_id: str,
    place_to_update: UpdatePlace,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
        return await place_service.update_place(repo, place_to_update, place_id)
    except PlaceNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Place"))
    except Exception as e: raise e



@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a Place", tags=["Admin Panel"])
async def delete_place(
    place_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    try:
         await place_service.delete_place(repo, place_id)
    except PlaceNotFoundError: raise HTTPException(404, detail=MESSAGE_404("Places"))
    except Exception as e: raise e

@router.post(
    "/review/{place_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add new review to a place",
    tags=["Place"]
)
async def add_new_review(
    place_id,
    new_review: review,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    if (str(new_review.user_id) == str(current_user.id)):
        try:
            return await place_service.add_review(repo, place_id, new_review)
        except Exception as e:
            raise e
    else:
        raise HTTPException(401, detail="Unautherized")


@router.delete(
    "/review/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review from a place",
    tags=["Admin Panel"]
)
async def delete_review(
    review: review,
    place_id: str,
    current_user: UserResponse = Security(
        get_current_user,
        scopes=[Role.USER["name"], Role.SUPER_ADMIN["name"], Role.ADMIN["name"]],
    ),
):
    if (
        str(review.user_id) == str(current_user.id)
        or current_user.user_role == Role.ADMIN["name"]
        or current_user.user_role == Role.SUPER_ADMIN["name"]
    ):
        try:
            await place_service.delete_review(repo, place_id, review)
        except Exception as e:
            if isinstance(e, PlaceNotFoundError):
                raise HTTPException(404, detail=MESSAGE_404("Place"))
            else:
                raise HTTPException(422, detail=str(e))
    else:
        raise HTTPException(401, detail="Unautherized")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            res = await place_service.search_places(repo, data)
            if res is not None:
                await websocket.send_json(res.json())
            else:
                await websocket.send_json(json.dumps({
                            "errors": [
                                "Place not exist"
                            ],
                            "status_code": "404"
                            }))        
    except Exception as e:
        await websocket.close()    
