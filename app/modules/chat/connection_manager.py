import asyncio
from collections import defaultdict

from fastapi import WebSocket


class DealChatConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[int, dict[int, set[WebSocket]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self._lock = asyncio.Lock()

    async def connect(
        self,
        deal_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None:
        await websocket.accept()
        async with self._lock:
            self._rooms[deal_id][user_id].add(websocket)

    async def disconnect(
        self,
        deal_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None:
        async with self._lock:
            room = self._rooms.get(deal_id)
            if not room:
                return

            user_connections = room.get(user_id)
            if not user_connections:
                return

            user_connections.discard(websocket)

            if not user_connections:
                del room[user_id]
            if not room:
                del self._rooms[deal_id]

    def is_user_connected(self, deal_id: int, user_id: int) -> bool:
        room = self._rooms.get(deal_id)
        if not room:
            return False
        return bool(room.get(user_id))

    async def broadcast_json(
            self,
            deal_id: int,
            payload: dict,
            exclude_user_id: int | None = None
    ) -> None:
        # Собираем цели С user_id для безопасного disconnect
        async with self._lock:
            room = self._rooms.get(deal_id, {})
            # Храним пару (websocket, user_id)
            targets: list[tuple[WebSocket, int]] = []
            for uid, connections in room.items():
                if uid == exclude_user_id:
                    continue
                for ws in connections:
                    targets.append((ws, uid))

        # Отправляем с сохранённым user_id
        for ws, uid in targets:
            try:
                await ws.send_json(payload)
            except Exception:
                # Теперь user_id известен точно
                await self.disconnect(deal_id, uid, ws)


deal_chat_manager = DealChatConnectionManager()
