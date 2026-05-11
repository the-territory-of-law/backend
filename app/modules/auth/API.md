# Auth API

Базовый префикс: `/auth`.

## Эндпоинты

### `POST /auth/register`
- Создает нового пользователя и выставляет auth-cookie.
- Body (`application/json`): поля `UserCreate` (`name`, `email`, `password`, `role`).
- Успех: `200`, `{ "message": "Registered successfully", "user": ... }`.

### `POST /auth/login`
- Авторизация по форме и выставление auth-cookie.
- Body (`application/x-www-form-urlencoded`): `username`, `password`.
- Успех: `200`, `{ "message": "Logged in successfully" }`.
- Ошибка: `401` при неверных учетных данных.

### `POST /auth/refresh`
- Обновляет access token по refresh-cookie.
- Требует cookie `refresh_token`.
- Успех: `200`, `{ "message": "Token refreshed" }`.
- Ошибки: `401` (`No refresh token`, `Invalid refresh token`).

### `POST /auth/logout`
- Очищает auth cookies текущего пользователя.
- Успех: `200`, `{ "message": "Logged out" }`.
