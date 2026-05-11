# Disputes API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/disputes`.

## Эндпоинты

### `POST /disputes`
- Открыть спор по сделке.
- Body: `deal_id`, `reason`, `description`.
- Response: `201`, объект спора.

### `GET /disputes/{dispute_id}`
- Получить спор по ID.
- Response: `200`, объект спора.

### `GET /disputes`
- Список споров.
- Query: `deal_id`, `status` (`open|in_review|resolved|rejected`), `limit`, `offset`.
- Response: `200`, массив споров.

### `POST /disputes/{dispute_id}/messages`
- Добавить комментарий/позицию стороны в спор.
- Body: `text`, `attachments[]?`.
- Response: `201`, сообщение спора.

### `GET /disputes/{dispute_id}/timeline`
- История действий по спору (создание, комментарии, смена статуса, решение).
- Response: `200`, массив событий.

## Админ-эндпоинты по спорам

### `POST /admin/disputes/{dispute_id}/assign`
- Назначить админа-резолвера.
- Body: `admin_user_id`.
- Response: `200`, спор с `assigned_admin_id`.

### `POST /admin/disputes/{dispute_id}/request-info`
- Запросить доп. информацию у сторон.
- Body: `text`, `deadline_at?`.
- Response: `200`, обновленный спор.

### `POST /admin/disputes/{dispute_id}/resolve`
- Финальное решение спора админом.
- Body: `resolution`, `refund_amount?`, `winner_side?`, `comment`.
- Response: `200`, спор со статусом `resolved`.

### `POST /admin/disputes/{dispute_id}/reject`
- Закрыть спор без удовлетворения требований.
- Body: `reason`.
- Response: `200`, спор со статусом `rejected`.
