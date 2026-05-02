from fastapi import WebSocket
from typing import Set


class InventoryConnectionManager:
    """
    Manejador de conexiones WebSocket activas.
    Almacena en memoria todos los clientes conectados
    y permite notificarlos a todos con un broadcast.
    """
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: str):
        #Envía el mensaje a todos los clientes conectados
        dead = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                #Si la conexión falló, la marcamos para removerla
                dead.add(connection)
        for connection in dead:
            self.active_connections.discard(connection)

manager = InventoryConnectionManager()