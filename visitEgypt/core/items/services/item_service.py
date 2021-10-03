

from visitEgypt.core.items.protocols.item_repo import ItemRepo

from ..protocols.item_repo import ItemRepo

async def create(
    repo: ItemRepo, st: str,
) -> str:
    return await repo.testrepo(st)