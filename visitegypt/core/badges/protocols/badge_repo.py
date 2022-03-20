from typing import Dict, Protocol
from visitegypt.core.badges.entities.badge import (
    BadgeBase,
    BadgeTask,
    BadgesPageResponse,
    BadgeInDB,
    BadgeUpdate
)

class BadgeRepo(Protocol):
    async def get_filtered_badges(
        self, page_num: int, limit: int, filters: Dict
    ) -> BadgesPageResponse:
        pass

    async def create_badge(self, Badge_to_create: BadgeBase) -> BadgeInDB:
        pass

    async def update_badge(badge_to_update: BadgeUpdate, badge_id: str) -> BadgeInDB:
        pass

    async def delete_badge(self, badge_id: str) -> bool:
        pass