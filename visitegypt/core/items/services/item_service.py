

from visitegypt.core.items.protocols.item_repo import ItemRepo

from visitegypt.core.items.protocols.item_repo import ItemRepo

async def create(
    repo: ItemRepo, st: str,
) -> str:
    return await repo.testrepo(st)