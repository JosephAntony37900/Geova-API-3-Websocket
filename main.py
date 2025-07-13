from fastapi import FastAPI
import uvicorn
import threading

from core.config import get_rabbitmq_config
from Websocket.infraestructure.dependencies import init_ws_dependencies
from Websocket.infraestructure.routes.routes_ws import router as ws_router
from Websocket.infraestructure.consumers.rabbit_consumer import consume_messages

app = FastAPI()
@app.get("/")
def root():
    return {"message": "Geova WebSocket API está corriendo correctamente 🚀"}

# Obtener configuración
rabbitmq_config = get_rabbitmq_config()

# Inicializar manager y usecase
usecase = init_ws_dependencies(app)

@app.on_event("startup")
def start_consumer():
    t = threading.Thread(target=consume_messages, args=(usecase, rabbitmq_config), daemon=True)
    t.start()

# Ruta WebSocket
app.include_router(ws_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
