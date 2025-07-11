from abc import ABC, abstractmethod

class Broadcaster(ABC):
    @abstractmethod
    async def broadcast(self, message: dict): pass
