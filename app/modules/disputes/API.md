# Disputes API

Документация по спорам по сделкам.

Статус: **предлагаемый API (draft, HTTP ещё не реализован)**.

Базовый префикс: `/disputes`.

Админ-эндпоинты: `/admin/disputes/...` (роль `admin`).

## Статусы спора

| Значение | Описание |
|---|---|
| `open` | Спор открыт |
| `resolved` | Решение вынесено |

## Решение (resolution)

| Значение | Описание |
|---|---|
| `client_win` | В пользу клиента |
| `lawyer_win` | В пользу юриста |
| `draw` | Компромисс / без явного победителя |

---

## Открыть спор

```http
POST /disputes
```

Участник сделки.

### Тело запроса

```json
{
  "deal_id": 201,
  "reason": "Услуга не оказана в срок"
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `deal_id` | `integer` | Да | ID сделки |
| `reason` | `string` | Да | Причина |

### Ответ `201`

```json
{
  "id": 7,
  "deal_id": 201,
  "opened_by": 20,
  "status": "open",
  "reason": "Услуга не оказана в срок",
  "resolution": "draw",
  "created_at": "2026-05-12T14:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Спор по сделке уже открыт |
| `401` | Не авторизован |
| `403` | Не участник сделки |
| `404` | Сделка не найдена |
| `422` | Валидация |

---

## Получить спор

```http
GET /disputes/{dispute_id}
```

### Ответ `200`

```json
{
  "id": 7,
  "deal_id": 201,
  "opened_by": 20,
  "status": "open",
  "reason": "Услуга не оказана в срок",
  "resolution": "draw",
  "created_at": "2026-05-12T14:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа |
| `404` | Спор не найден |

---

## Список споров

```http
GET /disputes
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | Фильтр по сделке |
| `status` | `string` | `open`, `resolved` |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "disputes": [
    {
      "id": 7,
      "deal_id": 201,
      "opened_by": 20,
      "status": "open",
      "reason": "Услуга не оказана в срок",
      "resolution": "draw",
      "created_at": "2026-05-12T14:00:00Z"
    }
  ],
  "total": 1,
  "has_more": false
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `400` | Некорректный `status` |

---

## Сообщение в споре

```http
POST /disputes/{dispute_id}/messages
```

### Тело запроса

```json
{
  "text": "Прикладываю переписку и доказательства",
  "attachment_ids": [801, 802]
}
```

### Ответ `201`

```json
{
  "id": 31,
  "dispute_id": 7,
  "author_id": 20,
  "text": "Прикладываю переписку и доказательства",
  "attachments": [
    {
      "id": 801,
      "url": "/static/files/801.pdf",
      "filename": "chat_export.pdf",
      "mime": "application/pdf",
      "size": 102400
    }
  ],
  "created_at": "2026-05-12T15:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Пустой текст и нет вложений |
| `401` | Не авторизован |
| `403` | Нет доступа к спору |
| `404` | Спор не найден |

---

## Таймлайн спора

```http
GET /disputes/{dispute_id}/timeline
```

### Ответ `200`

```json
{
  "events": [
    {
      "type": "dispute_opened",
      "at": "2026-05-12T14:00:00Z",
      "actor_id": 20,
      "payload": { "reason": "Услуга не оказана в срок" }
    },
    {
      "type": "message_added",
      "at": "2026-05-12T15:00:00Z",
      "actor_id": 20,
      "payload": { "message_id": 31 }
    }
  ]
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа |
| `404` | Спор не найден |

---

# Админ: назначить резолвера

```http
POST /admin/disputes/{dispute_id}/assign
```

### Тело запроса

```json
{
  "admin_user_id": 1
}
```

### Ответ `200`

Объект спора с полем `assigned_admin_id`.

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Не admin |
| `404` | Спор не найден |

---

# Админ: запросить информацию

```http
POST /admin/disputes/{dispute_id}/request-info
```

### Тело запроса

```json
{
  "text": "Предоставьте акт выполненных работ",
  "deadline_at": "2026-05-20T18:00:00Z"
}
```

### Ответ `200`

Обновлённый спор + событие в timeline.

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |
| `404` | Не найден |

---

# Админ: решить спор

```http
POST /admin/disputes/{dispute_id}/resolve
```

### Тело запроса

```json
{
  "resolution": "client_win",
  "refund_amount": 45000,
  "comment": "Работы не подтверждены"
}
```

### Ответ `200`

```json
{
  "id": 7,
  "deal_id": 201,
  "opened_by": 20,
  "status": "resolved",
  "reason": "Услуга не оказана в срок",
  "resolution": "client_win",
  "created_at": "2026-05-12T14:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Спор уже закрыт |
| `403` | Не admin |
| `404` | Не найден |
| `422` | Невалидный `resolution` |

---

# Админ: отклонить спор

```http
POST /admin/disputes/{dispute_id}/reject
```

### Тело запроса

```json
{
  "reason": "Недостаточно оснований"
}
```

### Ответ `200`

Спор со статусом `resolved`, resolution по правилам платформы.

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не admin |
| `404` | Не найден |

---

# Структуры данных

```ts
type Dispute = {
  id: number
  deal_id: number
  opened_by: number
  status: 'open' | 'resolved'
  reason: string
  resolution: 'client_win' | 'lawyer_win' | 'draw'
  created_at: string
  assigned_admin_id?: number | null
}

type DisputeMessage = {
  id: number
  dispute_id: number
  author_id: number
  text: string
  attachments: FileMeta[]
  created_at: string
}

type TimelineEvent = {
  type: string
  at: string
  actor_id: number
  payload: Record<string, unknown>
}
```
