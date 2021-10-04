from typing import Protocol
from typing import Protocol

class ItemRepo (Protocol):
   async def testrepo(self, t: str) -> str:
      pass