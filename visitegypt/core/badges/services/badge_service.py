from typing import Dict, Optional
from visitegypt.core.badges.entities.badge import (
    BadgeBase,
    BadgeTask,
    BadgeInDB,
    BadgesPageResponse,
    BadgeUpdate
)
from visitegypt.core.badges.protocols.badge_repo import BadgeRepo
from visitegypt.core.errors.badge_error import BadgeNotFoundError, BadgeAlreadyExists

async def get_filtered_badges(
    repo: BadgeRepo, page_num: int = 1, limit: int = 15, filters: Dict = None
) -> BadgesPageResponse:
    try:
        badges = await repo.get_filtered_badges(
            page_num=page_num, limit=limit, filters=filters
        )
        if badges:
            return badges
        raise BadgeNotFoundError
    except BadgeNotFoundError as ie:
        raise ie
    except Exception as e:
        raise e

async def create_badge(repo: BadgeRepo, badge_to_create: BadgeBase) -> BadgeInDB:
    try:
        c_i = await get_filtered_badges(
            repo, page_num=1, limit=1, filters={"title": badge_to_create.title}
        )
        if c_i.badges[0]:
            raise BadgeAlreadyExists
    except BadgeAlreadyExists as iee:
        raise iee
    except BadgeNotFoundError:
        pass
    except Exception as e:
        raise e

    try:
        return await repo.create_badge(badge_to_create)
    except Exception as e:
        raise e

async def update_badge_by_id(
    repo: BadgeRepo, badge_to_update: BadgeUpdate, badge_id: str
) -> Optional[BadgeInDB]:
    try:
        return await repo.update_badge(ibadge_id=badge_id, badge_to_update=badge_to_update)
    except BadgeNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e

async def delete_badge_by_id(repo: BadgeRepo, badge_id: str) -> bool:
    try:
        return await repo.delete_badge(badge_id)
    except BadgeNotFoundError as ue:
        raise ue
    except Exception as e:
        raise e