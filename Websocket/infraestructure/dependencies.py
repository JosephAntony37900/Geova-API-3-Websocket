from infraestructure.ws.manager import ConnectionManager
from application.websocket_usecase import WebSocketUseCase

def init_ws_dependencies(app):
    manager = ConnectionManager()
    app.state.manager = manager
    usecase = WebSocketUseCase(manager)

    return usecase  # Para pasárselo al consumidor de Rabbit
