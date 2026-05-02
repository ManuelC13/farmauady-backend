from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websockets.manager import manager

router = APIRouter(tags=["websockets"])

@router.websocket("/ws/inventory")
async def inventory_websocket(websocket: WebSocket):
    """
    Canal WebSocket de inventario.
    Cada vendedor que abra la página de 'Nueva Venta' se conectará aquí.
    Recibirá el mensaje 'INVENTORY_UPDATE' cada vez que alguien
    reserve, libere o confirme una venta.
    """
    await manager.connect(websocket)
    try:
        #Se mantiene la conexión abierta esperando mensajes del cliente
        #(en este flujo el cliente no envía mensajes, solo los recibe)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
