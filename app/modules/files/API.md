# Files API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/files`.

## Эндпоинты

### `POST /files/upload`
- Загрузка файла.
- Body: `multipart/form-data` (`file`, `entity_type`, `entity_id`).
- Response: `201`, метаданные файла (`id`, `url`, `mime_type`, `size`).

### `POST /files/chat-upload`
- Загрузка вложения специально для чата.
- Body: `multipart/form-data` (`file`, `deal_id`).
- Ограничения: типы (`pdf`, `docx`, `jpg`, `png`), лимит размера (например, до 20MB).
- Response: `201`, `{ file_id, deal_id, url, mime_type, size }`.

### `GET /files/{file_id}`
- Получить метаданные файла.
- Response: `200`.

### `GET /files/{file_id}/download`
- Скачать файл.
- Response: `200`, бинарный поток.

### `GET /files`
- Список файлов по сущности.
- Query: `entity_type`, `entity_id`, `limit`, `offset`.
- Response: `200`, массив метаданных.

### `POST /files/{file_id}/attach-to-message`
- Привязать уже загруженный файл к сообщению чата.
- Body: `message_id`.
- Response: `200`, `{ message_id, file_id }`.

### `DELETE /files/{file_id}`
- Удалить файл (soft/hard delete по бизнес-правилам).
- Response: `204`.
