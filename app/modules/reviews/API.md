# Reviews API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/reviews`.

## Эндпоинты

### `POST /reviews`
- Оставить отзыв после завершения сделки.
- Body: `deal_id`, `target_user_id`, `rating` (1..5), `text`.
- Response: `201`, отзыв.

### `GET /reviews/{review_id}`
- Получить отзыв по ID.
- Response: `200`.

### `GET /reviews`
- Список отзывов.
- Query: `target_user_id`, `author_id`, `deal_id`, `rating_gte`, `limit`, `offset`.
- Response: `200`, массив отзывов.

### `PATCH /reviews/{review_id}`
- Обновить отзыв автором в ограниченное время.
- Body: `rating?`, `text?`.
- Response: `200`, обновленный отзыв.

### `DELETE /reviews/{review_id}`
- Удалить отзыв (модерация/админ).
- Response: `204`.
