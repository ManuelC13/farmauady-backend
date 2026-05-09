from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth.auth_service import get_user_from_websocket
from app.services.websockets.presence_manager import presence_manager

router = APIRouter(tags=["websockets"])


@router.websocket("/ws/presence")
async def presence_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    Canal WebSocket de presencia de usuarios en tiempo real.
    
    Flujo:
    1. Cliente se conecta después de autenticarse.
    2. Servidor valida la sesión con el token jwt para obtener user_id.
    3. Registra el usuario como online.
    4. Mantiene la conexión abierta escuchando heartbeats (pings).
    5. Envía broadcasts cuando la lista de online cambia.
    6. Al desconectar, remueve la conexión.
    """
    
    #Valida la sesión con las cookie HttpOnly del token de acceso
    user = get_user_from_websocket(websocket, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    user_id = user.id_user
    
    #Conecta al usuario
    await presence_manager.connect(user_id, websocket)
    
    #Notifica a todos que hay un usuario online nuevo mediante un broadcast
    await presence_manager.broadcast_online_list()
    
    try:
        #Manteniene la conexión abierta escuchando mensajes
        while True:
            data = await websocket.receive_text()
            
            if data == "PING":
                #Refresca el heartbeat del usuario
                presence_manager.refresh_heartbeat(user_id)
                #Responde al cliente
                await websocket.send_text("PONG")
            
            elif data == "GET_ONLINE":
                #Cliente solicita la lista actual
                await websocket.send_text(
                    f"ONLINE_USERS:{','.join(map(str, presence_manager.get_online_users()))}"
                )
    
    except WebSocketDisconnect:
        #El usuario se desconectó (cerró tab, navegó fuera, etc.)
        presence_manager.disconnect(user_id, websocket)
        
        #Notifica a todos que el usuario desconectó
        await presence_manager.broadcast_online_list()
    
    except Exception as e:
        #Error inesperado
        print(f"Error en WebSocket de presencia para user_id {user_id}: {e}")
        presence_manager.disconnect(user_id, websocket)
