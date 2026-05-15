# Deals API

Документация по REST API сделок между клиентом и юристом.

Статус: **предлагаемый API (draft, ещё не реализован в HTTP)**.  
Базовый префикс: `/deals`.

Сделка связывает заявку клиента (`request_id`) и принятое предложение юриста (`offer_id`).  
Чат привязан к сделке по `deal_id` (см. [Chat API](../chat/API.md)).

## Авторизация

Все запросы требуют авторизованного пользователя (cookie `access_token`, как в auth и chat).

---

## Модель сделки

| Поле | Тип | Описание |
|---|---|---|
| `id` | `integer` | ID сделки |
| `request_id` | `integer` | ID заявки клиента |
| `offer_id` | `integer` | ID принятого предложения юриста |
| `client_id` | `integer` | ID пользователя-клиента (из заявки) |
| `lawyer_id` | `integer` | ID пользователя-юриста (из профиля по офферу) |
| `status` | `string` | Статус сделки |
| `amount` | `integer` | Сумма сделки (копейки или условные единицы — как в БД) |
| `platform_fee` | `integer` | Комиссия платформы |
| `lawyer_amount` | `integer` | Сумма юристу |
| `paid_at` | `string \| null` | Дата оплаты (ISO 8601) или `null` |
| `request` | `object` | Краткие данные заявки (заголовок, описание) |

## Статусы сделки

| Значение | Описание |
|---|---|
| `in_progress` | Сделка активна (в списке чатов может отображаться как `active`) |
| `completed` | Сделка завершена |
| `cancelled` | Сделка отменена |

---

# REST API

## Создать сделку

```http
POST /deals
```

Создаёт сделку на основе принятого предложения.  
После создания доступен чат: `GET /chats`, WebSocket `/ws/deals/{deal_id}/chat`.

### Тело запроса

```json
{
  "offer_id": 55
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `offer_id` | `integer` | Да | ID предложения в статусе `accepted` |

### Ответ `201`

```json
{
  "id": 201,
  "request_id": 40,
  "offer_id": 55,
  "client_id": 20,
  "lawyer_id": 10,
  "status": "in_progress",
  "amount": 50000,
  "platform_fee": 5000,
  "lawyer_amount": 45000,
  "paid_at": null,
  "request": {
    "id": 40,
    "title": "Развод и раздел имущества",
    "description": "Нужна консультация и сопровождение",
    "category": "devorce"
  }
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Оффер не в статусе `accepted` или по заявке уже есть сделка |
| `401` | Не авторизован |
| `403` | Нет прав создать сделку по этому офферу |
| `404` | Оффер или заявка не найдены |
| `422` | Невалидное тело запроса |

---

## Получить сделку по ID

```http
GET /deals/{deal_id}
```

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Ответ `200`

```json
{
  "id": 201,
  "request_id": 40,
  "offer_id": 55,
  "client_id": 20,
  "lawyer_id": 10,
  "status": "in_progress",
  "amount": 50000,
  "platform_fee": 5000,
  "lawyer_amount": 45000,
  "paid_at": null,
  "request": {
    "id": 40,
    "title": "Развод и раздел имущества",
    "description": "Нужна консультация и сопровождение",
    "category": "devorce"
  }
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Пользователь не участник сделки |
| `404` | Сделка не найдена |

---

## Список сделок текущего пользователя

```http
GET /deals
```

Возвращает сделки, где текущий пользователь — клиент или юрист.

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `status` | `string` | Фильтр: `in_progress`, `completed`, `cancelled` |
| `role` | `string` | `client` или `lawyer` — с какой стороны участвует пользователь |
| `limit` | `integer` | Количество записей (по умолчанию `50`, макс. `100`) |
| `offset` | `integer` | Смещение для пагинации |

### Ответ `200`

```json
{
  "deals": [
    {
      "id": 201,
      "request_id": 40,
      "offer_id": 55,
      "client_id": 20,
      "lawyer_id": 10,
      "status": "in_progress",
      "amount": 50000,
      "platform_fee": 5000,
      "lawyer_amount": 45000,
      "paid_at": null,
      "request": {
        "id": 40,
        "title": "Развод и раздел имущества",
        "description": "Нужна консультация и сопровождение",
        "category": "devorce"
      }
    },
    {
      "id": 198,
      "request_id": 38,
      "offer_id": 52,
      "client_id": 20,
      "lawyer_id": 11,
      "status": "completed",
      "amount": 30000,
      "platform_fee": 3000,
      "lawyer_amount": 27000,
      "paid_at": "2026-05-01T12:00:00Z",
      "request": {
        "id": 38,
        "title": "Трудовой спор",
        "description": null,
        "category": "devorce"
      }
    }
  ],
  "total": 12,
  "has_more": true
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `400` | Некорректный `status` или `role` |

---

## Обновить сделку

```http
PATCH /deals/{deal_id}
```

Обновляет финансовые поля сделки. Заголовок и описание меняются через API заявок, не через сделку.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Тело запроса

Все поля опциональны; передаются только изменяемые.

```json
{
  "amount": 55000,
  "platform_fee": 5500,
  "lawyer_amount": 49500
}
```

| Поле | Тип | Описание |
|---|---|---|
| `amount` | `integer` | Сумма сделки |
| `platform_fee` | `integer` | Комиссия платформы |
| `lawyer_amount` | `integer` | Сумма юристу |

### Ответ `200`

```json
{
  "id": 201,
  "request_id": 40,
  "offer_id": 55,
  "client_id": 20,
  "lawyer_id": 10,
  "status": "in_progress",
  "amount": 55000,
  "platform_fee": 5500,
  "lawyer_amount": 49500,
  "paid_at": null,
  "request": {
    "id": 40,
    "title": "Развод и раздел имущества",
    "description": "Нужна консультация и сопровождение",
    "category": "devorce"
  }
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Пустое тело или некорректные значения |
| `401` | Не авторизован |
| `403` | Нет прав редактировать сделку |
| `404` | Сделка не найдена |
| `422` | Валидация не пройдена |

---

## Сменить статус сделки

```http
POST /deals/{deal_id}/status
```

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Тело запроса

```json
{
  "status": "completed"
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `status` | `string` | Да | `in_progress`, `completed` или `cancelled` |

### Ответ `200`

```json
{
  "id": 201,
  "request_id": 40,
  "offer_id": 55,
  "client_id": 20,
  "lawyer_id": 10,
  "status": "completed",
  "amount": 50000,
  "platform_fee": 5000,
  "lawyer_amount": 45000,
  "paid_at": "2026-05-10T18:00:00Z",
  "request": {
    "id": 40,
    "title": "Развод и раздел имущества",
    "description": "Нужна консультация и сопровождение",
    "category": "devorce"
  }
}
```

При переходе в `completed` бэкенд может проставить `paid_at`, если оплата уже прошла.

### Ошибки

| Код | Описание |
|---|---|
| `400` | Недопустимый переход статуса (например, из `cancelled` в `in_progress`) |
| `401` | Не авторизован |
| `403` | Нет прав менять статус |
| `404` | Сделка не найдена |
| `422` | Неизвестное значение `status` |

---

## Данные чата сделки

```http
GET /deals/{deal_id}/chat
```

Возвращает ссылки и метаданные для подключения к чату сделки.  
Сообщения загружаются через `GET /chats/{deal_id}/messages` (см. Chat API).

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Ответ `200`

```json
{
  "deal_id": 201,
  "client_id": 20,
  "lawyer_id": 10,
  "ws_path": "/ws/deals/201/chat",
  "messages_count": 42,
  "unread_count": 3
}
```

| Поле | Описание |
|---|---|
| `deal_id` | ID сделки (ключ чата) |
| `client_id` | ID клиента |
| `lawyer_id` | ID юриста |
| `ws_path` | Путь WebSocket (без хоста; авторизация — cookie или `?token=`) |
| `messages_count` | Всего сообщений в чате |
| `unread_count` | Непрочитанных для текущего пользователя |

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Пользователь не участник сделки |
| `404` | Сделка не найдена |

---

# Структуры данных

## Deal

```ts
type Deal = {
  id: number
  request_id: number
  offer_id: number
  client_id: number
  lawyer_id: number
  status: 'in_progress' | 'completed' | 'cancelled'
  amount: number
  platform_fee: number
  lawyer_amount: number
  paid_at: string | null
  request: DealRequestSummary
}
```

## DealRequestSummary

```ts
type DealRequestSummary = {
  id: number
  title: string
  description: string | null
  category: string
}
```

## DealsPage

```ts
type DealsPage = {
  deals: Deal[]
  total: number
  has_more: boolean
}
```

## DealStatusChangeRequest

```ts
type DealStatusChangeRequest = {
  status: 'in_progress' | 'completed' | 'cancelled'
}
```

## DealChatInfo

```ts
type DealChatInfo = {
  deal_id: number
  client_id: number
  lawyer_id: number
  ws_path: string
  messages_count: number
  unread_count: number
}
```

---

# Связь с чатом

- Список диалогов: `GET /chats` (поле `deal_id`, `deal_status`).
- История: `GET /chats/{deal_id}/messages`.
- Realtime: `WS {ws_path}` → например `ws://host/ws/deals/201/chat`.
- Прочитать до сообщения: `POST /chats/{deal_id}/read-through`.

Отдельной сущности `chat_id` в БД нет: чат идентифицируется по `deal_id`.

---

# Важные правила

- Участник сделки — только клиент заявки и юрист из принятого оффера.
- Создание сделки обычно выполняется после `accepted` оффера, не «с нуля» без заявки.
- Отменённую сделку (`cancelled`) повторно в работу без отдельного бизнес-сценария не переводят.
- Финансовые поля (`amount`, `platform_fee`, `lawyer_amount`) задаются при создании и могут обновляться через `PATCH`.
- HTTP-роуты из этого документа **ещё не подключены** к приложению; для чата и auth используйте реализованные модули.
