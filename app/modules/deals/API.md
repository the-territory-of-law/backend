# Deals API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/deals`.

## Эндпоинты

### `POST /deals`
- Создать сделку.
- Body: `title`, `description`, `client_id`, `lawyer_id`, `amount`.
- Response: `201`, объект сделки.
- Побочный эффект: автоматически создается чат сделки (`deal_chat`) и связывается с `deal_id`.

### `GET /deals/{deal_id}`
- Получить сделку по ID.
- Response: `200`, объект сделки.
- Ошибка: `404`, если не найдена.

### `GET /deals`
- Список сделок текущего пользователя.
- Query: `status`, `role` (`client|lawyer`), `limit`, `offset`.
- Response: `200`, массив сделок.

### `PATCH /deals/{deal_id}`
- Обновить поля сделки (например, `title`, `description`, `amount`).
- Response: `200`, обновленная сделка.

### `POST /deals/{deal_id}/status`
- Смена статуса сделки.
- Body: `status` (`pending|active|completed|cancelled`).
- Response: `200`, объект сделки с новым статусом.

### `GET /deals/{deal_id}/chat`
- Получить данные связанного чата сделки.
- Response: `200`, `{ deal_id, chat_id, ws_path, messages_count }`.
