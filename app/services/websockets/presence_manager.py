from fastapi import WebSocket
from typing import Dict, Set, List
from datetime import datetime, timedelta
import asyncio

"""
    Gestiona la presencia de usuarios conectados en tiempo real a través de los websockets. 
    Permite rastrear qué usuarios están online, manejar múltiples conexiones por usuario (pestañas/dispositivos) 
    y enviar actualizaciones a todos los admins cuando la lista de usuarios online cambia.
"""
class PresenceManager:

    def __init__(self):
        # user_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # user_id -> datetime (última actividad)
        self.last_seen: Dict[int, datetime] = {}
        # timeout en segundos para considerar inactivo
        self.heartbeat_timeout = 120  # 2 minutos

    #Conecta un WebSocket para un usuario. Si el usuario no existe en el mapa, se crea.
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.last_seen[user_id] = datetime.utcnow()

    #Desconecta un WebSocket específico de un usuario. Si el usuario no tiene más conexiones, lo remueve del mapa.
    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            #Si el usuario no tiene más conexiones, remover la entrada
            if len(self.active_connections[user_id]) == 0:
                del self.active_connections[user_id]
                if user_id in self.last_seen:
                    del self.last_seen[user_id]

    #Retorna la lista de user_id de los usuarios que tienen al menos una conexión activa.
    def get_online_users(self) -> List[int]:
        return sorted(list(self.active_connections.keys()))

    #Retorna cuántas conexiones activas tiene un usuario específico.
    def get_user_connection_count(self, user_id: int) -> int:
        return len(self.active_connections.get(user_id, set()))

    #Verifica si un usuario está online (tiene al menos una conexión activa).
    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    #Broadcart para enviar la lista actualizada a todos los usuarios conectados.
    async def broadcast_online_list(self):
        online_users = self.get_online_users()
        message = f"ONLINE_USERS:{','.join(map(str, online_users))}"
        
        dead_connections = []
        
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    #Marcar para remover si falló el envío
                    dead_connections.append((user_id, connection))
        
        #Limpiar conexiones muertas
        for user_id, connection in dead_connections:
            self.disconnect(user_id, connection)

    #Función para verificar conexiones inactivas y limpiarlas. Se llama periódicamente.
    async def heartbeat_check(self):
        now = datetime.utcnow()
        users_to_remove = []
        
        for user_id, last_time in self.last_seen.items():
            elapsed = (now - last_time).total_seconds()
            if elapsed > self.heartbeat_timeout:
                users_to_remove.append(user_id)
        
        #Remover conexiones expiradas
        for user_id in users_to_remove:
            if user_id in self.active_connections:
                connections = list(self.active_connections[user_id])
                for connection in connections:
                    try:
                        await connection.close()
                    except Exception:
                        pass
                del self.active_connections[user_id]
                del self.last_seen[user_id]

    #Refresca el timestamp de última actividad de un usuario. Se llama cuando el cliente envía un heartbeat (ping).
    def refresh_heartbeat(self, user_id: int):
        if user_id in self.last_seen:
            self.last_seen[user_id] = datetime.utcnow()

    #Retorna el total de usuarios online (con al menos una conexión activa).
    def get_online_count(self) -> int:
        return len(self.active_connections)


#Instancia global del manager de presencia
presence_manager = PresenceManager()
