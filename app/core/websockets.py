from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, List[WebSocket]]= {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept() 
        # Если юзера еще нет — создаем пустой список
        if user_id not in self.active_connections:
            self.active_connections[user_id] = [] 
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            # Если у пользователя больше нет открытых сокетов, удаляем ключ
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        """Отправить сообщение конкретному пользователю на все его устройства"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()