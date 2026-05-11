# Admin API

Статус: **предлагаемый API (draft, еще не реализован)**.
Базовый префикс: `/admin`.

## Эндпоинты

### `GET /admin/dashboard`
- Сводная статистика платформы.
- Response: `200`, агрегаты (пользователи, сделки, споры, выручка).

### `GET /admin/users`
- Админ-список пользователей.
- Query: `role`, `status`, `search`, `limit`, `offset`.
- Response: `200`, массив пользователей.

### `POST /admin/users/{user_id}/ban`
- Заблокировать пользователя.
- Body: `reason`, `until?`.
- Response: `200`, пользователь с новым статусом.

### `POST /admin/users/{user_id}/unban`
- Снять блокировку пользователя.
- Response: `200`.

### `GET /admin/audit-logs`
- Получить журнал админ-действий.
- Query: `actor_id`, `action`, `from`, `to`, `limit`, `offset`.
- Response: `200`, массив событий аудита.

### `GET /admin/lawyer-verifications`
- Список заявок на проверку дипломов.
- Query: `status` (`pending|approved|rejected`), `limit`, `offset`.
- Response: `200`, массив заявок на верификацию.

### `GET /admin/lawyer-verifications/{profile_id}`
- Детали заявки: данные профиля, диплом, история проверок.
- Response: `200`.

### `POST /admin/lawyer-verifications/{profile_id}/approve`
- Подтвердить диплом и активировать профиль юриста.
- Body: `comment?`.
- Response: `200`.

### `POST /admin/lawyer-verifications/{profile_id}/reject`
- Отклонить диплом.
- Body: `reason`.
- Response: `200`.
