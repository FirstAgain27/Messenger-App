from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[int, List[WebSocket]] = {}

    # Подключиться к WebSocket
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    # Отключиться от WebSocket
    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    # Отправить персоанльное сообщение 
    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

    # Отправить сообщение всем участникам чата (кроме исключённого)
    async def broadcast_to_chat(self, chat_id: int, message: dict, participant_ids: List[int], exclude_user_id: int = None):
        for user_id in participant_ids:
            if user_id == exclude_user_id:
                continue
            await self.send_personal_message(user_id, message)

manager = ConnectionManager()