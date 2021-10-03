from abc import ABC, abstractmethod
from typing import Type, Callable
from fastapi import Depends

class BaseRepo():
    def __init__ (self, st: str):
        self._st = st
   
    @property
    def connection (self) -> str:
        return self._st


class UserRepo(ABC, BaseRepo):
    @abstractmethod
    def createUser(self, name: str) -> str:
        pass

class UserRepoImpl(UserRepo):

    def __init__(self, st: str):
        super().__init__(st)
        self.pp = "ppp"
        
    def createUser(self, name: str) -> str:
        return f'This is a test {name}, {self._st}, {self.pp}'



def _get_db_pool(request: str) -> str:
    return request




def get_repository(
    repo_type: Type[BaseRepo],
) -> Callable[[str], BaseRepo]:
    def _get_repo(
        conn: str = Depends(_get_db_pool),
    ) -> BaseRepo:
        return repo_type(conn)

    return _get_repo

#user = UserRepoImpl('Ahmed')


userR = get_repository(UserRepoImpl)

print(userR().createUser('Ahmed'))
