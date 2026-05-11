# Requests API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/requests`.

## Эндпоинты

### `POST /requests`
- Создать юридическую заявку.
- Body: `title`, `description`, `budget_min`, `budget_max`, `category`, `deadline`.
- Response: `201`, заявка.

### `GET /requests/{request_id}`
- Получить заявку по ID.
- Response: `200`.

### `GET /requests`
- Список заявок.
- Query: `status`, `category`, `budget_min`, `budget_max`, `limit`, `offset`.
- Response: `200`, массив заявок.

### `PATCH /requests/{request_id}`
- Обновить заявку владельцем.
- Response: `200`, обновленная заявка.

### `POST /requests/{request_id}/close`
- Закрыть заявку (например, после выбора оффера).
- Body: `reason?`.
- Response: `200`, заявка с финальным статусом.
