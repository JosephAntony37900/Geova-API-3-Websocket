from Websocket.infraestructure.ws.manager import ConnectionManager
from Websocket.application.websocket_usecase import WebSocketUseCase

def init_ws_dependencies(app):
    manager = ConnectionManager()
    app.state.manager = manager
    usecase = WebSocketUseCase(manager)
    return usecase
