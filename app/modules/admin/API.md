# Admin API

Документация по административным операциям.

Статус: **предлагаемый API (draft, HTTP ещё не реализован)**.

Базовый префикс: `/admin`.

Все эндпоинты требуют роль `admin` и cookie / token авторизации.

---

## Дашборд

```http
GET /admin/dashboard
```

### Ответ `200`

```json
{
  "users_total": 1250,
  "users_active_7d": 340,
  "deals_total": 890,
  "deals_in_progress": 120,
  "disputes_open": 8,
  "revenue_total": 12500000,
  "lawyer_verifications_pending": 5
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Не admin |

---

## Список пользователей

```http
GET /admin/users
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `role` | `string` | `client`, `lawyer`, `admin` |
| `status` | `string` | `active`, `banned` |
| `search` | `string` | Поиск по email / имени |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "users": [
    {
      "id": 20,
      "email": "ivan@example.com",
      "username": "Иван Петров",
      "role": "client",
      "status": "active",
      "created_at": "2026-04-01T08:00:00Z"
    }
  ],
  "total": 1250,
  "has_more": true
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |

---

## Заблокировать пользователя

```http
POST /admin/users/{user_id}/ban
```

### Тело запроса

```json
{
  "reason": "Нарушение правил платформы",
  "until": "2026-12-31T23:59:59Z"
}
```

| Поле | Тип | Обязательное |
|---|---|---|
| `reason` | `string` | Да |
| `until` | `string` | Нет | ISO 8601; без поля — бессрочно |

### Ответ `200`

```json
{
  "id": 20,
  "email": "ivan@example.com",
  "username": "Иван Петров",
  "role": "client",
  "status": "banned",
  "banned_until": "2026-12-31T23:59:59Z",
  "ban_reason": "Нарушение правил платформы"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Уже заблокирован |
| `403` | Не admin |
| `404` | Пользователь не найден |

---

## Разблокировать пользователя

```http
POST /admin/users/{user_id}/unban
```

### Ответ `200`

```json
{
  "id": 20,
  "email": "ivan@example.com",
  "username": "Иван Петров",
  "role": "client",
  "status": "active",
  "banned_until": null,
  "ban_reason": null
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |
| `404` | Не найден |

---

## Журнал аудита

```http
GET /admin/audit-logs
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `actor_id` | `integer` | Кто выполнил действие |
| `action` | `string` | Код действия |
| `from` | `string` | Начало периода (ISO 8601) |
| `to` | `string` | Конец периода |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "logs": [
    {
      "id": 5001,
      "actor_id": 1,
      "action": "lawyer_verification.approve",
      "entity_type": "lawyer_profile",
      "entity_id": 3,
      "metadata": { "profile_id": 3 },
      "created_at": "2026-05-11T10:30:00Z"
    }
  ],
  "total": 100,
  "has_more": true
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |

---

## Заявки на верификацию дипломов

```http
GET /admin/lawyer-verifications
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `status` | `string` | `pending`, `approved`, `rejected` |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "items": [
    {
      "profile_id": 3,
      "user_id": 10,
      "username": "Алексей Смирнов",
      "verification_status": "pending",
      "submitted_at": "2026-05-10T12:00:00Z"
    }
  ],
  "total": 5,
  "has_more": false
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |

---

## Детали верификации

```http
GET /admin/lawyer-verifications/{profile_id}
```

### Ответ `200`

```json
{
  "profile": {
    "id": 3,
    "user_id": 10,
    "city": "Москва",
    "about": "Юрист по семейным делам",
    "experience_years": 8,
    "verification_status": "pending"
  },
  "diploma": {
    "file_id": 901,
    "url": "/static/files/901_diploma.pdf",
    "filename": "diploma.pdf"
  },
  "history": [
    {
      "status": "pending",
      "comment": null,
      "reviewed_by": null,
      "reviewed_at": "2026-05-10T12:00:00Z"
    }
  ]
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |
| `404` | Профиль не найден |

---

## Подтвердить диплом

```http
POST /admin/lawyer-verifications/{profile_id}/approve
```

### Тело запроса

```json
{
  "comment": "Документы в порядке"
}
```

### Ответ `200`

```json
{
  "profile_id": 3,
  "verification_status": "approved",
  "comment": "Документы в порядке",
  "reviewed_by": 1,
  "reviewed_at": "2026-05-11T11:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Уже `approved` |
| `403` | Не admin |
| `404` | Не найден |

---

## Отклонить диплом

```http
POST /admin/lawyer-verifications/{profile_id}/reject
```

### Тело запроса

```json
{
  "reason": "Диплом нечитаем, загрузите скан лучшего качества"
}
```

| Поле | Тип | Обязательное |
|---|---|---|
| `reason` | `string` | Да |

### Ответ `200`

```json
{
  "profile_id": 3,
  "verification_status": "rejected",
  "comment": "Диплом нечитаем, загрузите скан лучшего качества",
  "reviewed_by": 1,
  "reviewed_at": "2026-05-11T11:05:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |
| `404` | Не найден |
| `422` | Не передан `reason` |

---

# Связанные модули

- Споры: [Disputes API](../disputes/API.md) (`/admin/disputes/...`)
- Профили юристов: [Lawyer Profiles API](../lawyer_profiles/API.md)

---

# Структуры данных

```ts
type AdminDashboard = {
  users_total: number
  users_active_7d: number
  deals_total: number
  deals_in_progress: number
  disputes_open: number
  revenue_total: number
  lawyer_verifications_pending: number
}

type AdminUser = {
  id: number
  email: string
  username: string
  role: string
  status: 'active' | 'banned'
  banned_until?: string | null
  ban_reason?: string | null
  created_at?: string
}

type AuditLogEntry = {
  id: number
  actor_id: number
  action: string
  entity_type: string
  entity_id: number
  metadata: Record<string, unknown>
  created_at: string
}
```
