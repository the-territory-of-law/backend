# Offers API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/offers`.

## Эндпоинты

### `POST /offers`
- Создать оффер юриста на заявку.
- Body: `request_id`, `lawyer_id`, `price`, `comment`, `terms`.
- Response: `201`, оффер.

### `GET /offers/{offer_id}`
- Получить оффер по ID.
- Response: `200`.

### `GET /offers`
- Список офферов.
- Query: `request_id`, `lawyer_id`, `status` (`active|accepted|rejected|cancelled`), `limit`, `offset`.
- Response: `200`, массив офферов.

### `PATCH /offers/{offer_id}`
- Обновить оффер (до принятия клиентом).
- Response: `200`, обновленный оффер.

### `POST /offers/{offer_id}/accept`
- Принять оффер и инициировать создание сделки.
- Response: `200`, результат принятия (`offer` + `deal`).
