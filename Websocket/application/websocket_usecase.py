from domain.ports.broadcaster import Broadcaster

class WebSocketUseCase:
    def __init__(self, broadcaster: Broadcaster):
        self.broadcaster = broadcaster

    async def send_message(self, message: dict):
        await self.broadcaster.broadcast(message)
