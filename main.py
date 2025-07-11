# websocket_main.py
from fastapi import FastAPI
import uvicorn
import threading

from Websocket.infraestructure.dependencies import init_ws_dependencies
from Websocket.infraestructure.routes.routes_ws import router as ws_router
from Websocket.infraestructure.consumers.rabbit_consumer import consume_messages

app = FastAPI()

# Iniciar manager y usecase
usecase = init_ws_dependencies(app)

@app.on_event("startup")
def start_consumer():
    t = threading.Thread(target=consume_messages, args=(usecase,), daemon=True)
    t.start()

# Ruta de WebSocket
app.include_router(ws_router)

if __name__ == "__main__":
    uvicorn.run("websocket_main:app", host="0.0.0.0", port=8081, reload=True)
