from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, request: Request):
    manager = request.app.state.manager
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantiene conexión
    except WebSocketDisconnect:
        manager.disconnect(websocket)
