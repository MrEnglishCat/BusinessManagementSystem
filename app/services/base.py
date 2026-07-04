from abc import ABC, abstractmethod


class BaseService(ABC):

    repository = None

    @abstractmethod
    async def get(self): ...

    @abstractmethod
    async def add(self): ...

    @abstractmethod
    async def edit(self): ...

    @abstractmethod
    async def delete(self): ...
