# Chat API

HTTP-префикс: `/chats`.
WebSocket: `/ws/deals/{deal_id}/chat`.

Чат создается автоматически при создании сделки (`POST /deals`).

## HTTP эндпоинты

### `GET /chats`
- Возвращает список диалогов текущего пользователя.
- Query: `limit` (1..100, default `50`), `offset` (>=0, default `0`).
- Response: `200`, `ChatDialogResponse[]`.

### `GET /chats/{deal_id}/messages`
- Возвращает сообщения чата сделки.
- Доступ только участнику сделки.
- Query: `limit` (1..200, default `50`), `offset` (>=0, default `0`).
- Response: `200`, `ChatMessageResponse[]`.
- Ошибка: `403` (`Forbidden`).

### `POST /chats/{deal_id}/messages`
- Отправляет сообщение в чат сделки.
- Body: `{ "text": "...", "attachments": [file_id]? }` (`1..4000` символов).
- Response: `201`, `ChatMessageResponse`.
- Ошибки:
  - `403` — пользователь не участник сделки.
  - `422` — сообщение заблокировано off-platform guard.

### `POST /chats/{deal_id}/attachments`
- Загрузить файл-вложение в контексте чата.
- Body: `multipart/form-data` (`file`).
- Response: `201`, `{ file_id, url, mime_type, size }`.
- Далее `file_id` передается в `POST /chats/{deal_id}/messages`.

### `PATCH /chats/messages/{message_id}`
- Редактирует сообщение текущего пользователя.
- Body: `{ "text": "..." }`.
- Response: `200`, `ChatMessageResponse`.

### `DELETE /chats/messages/{message_id}`
- Удаляет сообщение текущего пользователя.
- Response: `204` (без тела).

## WebSocket протокол

### Подключение
- `GET ws(s)://<host>/ws/deals/{deal_id}/chat?token=<access_token>`
- Токен можно передать query-параметром `token` или через auth-cookie.

### Входящие события от клиента
- `{"type":"ping"}` -> ответ `{"type":"pong"}`.
- `{"type":"message","text":"..."}` -> сохранение и broadcast нового сообщения.

### События/ошибки от сервера
- `{"type":"message", ...}` — новое сообщение.
- `{"type":"error","detail":"invalid_json"}`.
- `{"type":"error","detail":"unknown_type"}`.
- `{"type":"error","detail":"empty_text"}`.
- `{"type":"error","detail":"off_platform_blocked","blocked_reason":"..."}`.

### Коды закрытия
- `4001` — не авторизован / некорректный токен / пользователь не найден.
- `4003` — нет доступа к сделке.
