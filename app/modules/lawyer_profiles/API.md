# Lawyer Profiles API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/lawyer-profiles`.

## Верификация диплома (обязательный этап)

- Профиль юриста получает статус `pending_verification` после загрузки диплома.
- До ручной проверки админом профиль не публикуется в общем поиске.
- После проверки статус меняется на `verified` или `rejected`.

## Эндпоинты

### `POST /lawyer-profiles`
- Создать профиль юриста.
- Body: `user_id`, `specializations[]`, `bio`, `experience_years`, `hour_rate`.
- Response: `201`, профиль.

### `POST /lawyer-profiles/{profile_id}/diploma`
- Загрузить диплом юриста.
- Body: `multipart/form-data` (`file`).
- Response: `201`, `{ diploma_file_id, verification_status: "pending_verification" }`.

### `GET /lawyer-profiles/{profile_id}`
- Получить профиль по ID.
- Response: `200`, профиль.

### `GET /lawyer-profiles`
- Поиск и фильтрация профилей.
- Query: `specialization`, `min_rate`, `max_rate`, `rating_gte`, `limit`, `offset`.
- Response: `200`, массив профилей.

### `PATCH /lawyer-profiles/{profile_id}`
- Обновить профиль юриста.
- Response: `200`, обновленный профиль.

### `GET /lawyer-profiles/{profile_id}/verification`
- Получить текущий статус проверки диплома.
- Response: `200`, `{ status, comment?, reviewed_by?, reviewed_at? }`.

### `POST /admin/lawyer-profiles/{profile_id}/verification/approve`
- Админ подтверждает диплом.
- Body: `comment?`.
- Response: `200`, профиль со статусом `verified`.

### `POST /admin/lawyer-profiles/{profile_id}/verification/reject`
- Админ отклоняет диплом.
- Body: `reason` (обязательно).
- Response: `200`, профиль со статусом `rejected`.
