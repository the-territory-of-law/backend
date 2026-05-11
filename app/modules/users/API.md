# Users API

Префикс не задан, маршруты объявлены как абсолютные (`/users...`).

## Эндпоинты

### `POST /users`
- Создает пользователя.
- Body: `UserCreate` (`name`, `email`, `password`, `role`).
- Response: `200` (объект пользователя из репозитория).

### `GET /users/{user_id}`
- Возвращает пользователя по ID.
- Response: `200`.

### `GET /users`
- Возвращает список пользователей с пагинацией.
- Query: `limit`, `offset` (через `PaginationParams`).
- Response: `200`.

### `PATCH /users/{user_id}`
- Обновляет пользователя.
- Body: `UserUpdate` (частичные поля `name`, `email`, `password`, `role`).
- Response: `200`.

### `DELETE /users/{user_id}`
- Удаляет пользователя.
- Response: `200` (формат зависит от `UserRepository.delete_user`).
