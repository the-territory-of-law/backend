# Offers API

Документация по предложениям юристов на заявки.

Статус: **предлагаемый API (draft, HTTP ещё не реализован)**.

Базовый префикс: `/offers`.

## Статусы оффера

| Значение | Описание |
|---|---|
| `pending` | Ожидает решения клиента |
| `accepted` | Принят клиентом (можно создавать сделку) |
| `rejected` | Отклонён |

---

## Создать оффер

```http
POST /offers
```

Роль `lawyer`, по открытой заявке.

### Тело запроса

```json
{
  "request_id": 40,
  "what_included": "Консультация, подготовка документов, представительство",
  "price": 50000,
  "term": "2026-06-15"
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `request_id` | `integer` | Да | ID заявки |
| `what_included` | `string` | Да | Что входит в услугу |
| `price` | `integer` | Да | Цена |
| `term` | `string` | Да | Срок (дата `YYYY-MM-DD`) |

### Ответ `201`

```json
{
  "id": 55,
  "request_id": 40,
  "lawyer_id": 10,
  "lawyer_profile_id": 3,
  "what_included": "Консультация, подготовка документов, представительство",
  "price": 50000,
  "term": "2026-06-15",
  "status": "pending"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Заявка закрыта или оффер уже есть |
| `401` | Не авторизован |
| `403` | Не юрист или нет профиля |
| `404` | Заявка не найдена |
| `422` | Валидация |

---

## Получить оффер

```http
GET /offers/{offer_id}
```

### Ответ `200`

```json
{
  "id": 55,
  "request_id": 40,
  "lawyer_id": 10,
  "lawyer_profile_id": 3,
  "what_included": "Консультация, подготовка документов",
  "price": 50000,
  "term": "2026-06-15",
  "status": "pending"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа |
| `404` | Не найден |

---

## Список офферов

```http
GET /offers
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `request_id` | `integer` | Фильтр по заявке |
| `lawyer_id` | `integer` | Фильтр по юристу (user id) |
| `status` | `string` | `pending`, `accepted`, `rejected` |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "offers": [
    {
      "id": 55,
      "request_id": 40,
      "lawyer_id": 10,
      "lawyer_profile_id": 3,
      "what_included": "Консультация, подготовка документов",
      "price": 50000,
      "term": "2026-06-15",
      "status": "pending"
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

## Обновить оффер

```http
PATCH /offers/{offer_id}
```

Только автор-юрист, пока `status` = `pending`.

### Тело запроса

```json
{
  "what_included": "Расширенный пакет услуг",
  "price": 55000,
  "term": "2026-06-20"
}
```

### Ответ `200`

Объект оффера (как в `GET /offers/{offer_id}`).

### Ошибки

| Код | Описание |
|---|---|
| `400` | Оффер не в `pending` |
| `401` | Не авторизован |
| `403` | Не автор |
| `404` | Не найден |
| `422` | Валидация |

---

## Принять оффер

```http
POST /offers/{offer_id}/accept
```

Клиент принимает оффер. Создаётся сделка (см. Deals API).

### Ответ `200`

```json
{
  "offer": {
    "id": 55,
    "request_id": 40,
    "lawyer_id": 10,
    "lawyer_profile_id": 3,
    "what_included": "Консультация, подготовка документов",
    "price": 50000,
    "term": "2026-06-15",
    "status": "accepted"
  },
  "deal": {
    "id": 201,
    "request_id": 40,
    "offer_id": 55,
    "client_id": 20,
    "lawyer_id": 10,
    "status": "in_progress",
    "amount": 50000,
    "platform_fee": 5000,
    "lawyer_amount": 45000,
    "paid_at": null
  }
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Оффер не `pending` или сделка уже есть |
| `401` | Не авторизован |
| `403` | Только клиент-владелец заявки |
| `404` | Оффер не найден |
| `409` | Конфликт статусов |

---

# Структуры данных

```ts
type Offer = {
  id: number
  request_id: number
  lawyer_id: number
  lawyer_profile_id: number
  what_included: string
  price: number
  term: string
  status: 'pending' | 'accepted' | 'rejected'
}

type OffersPage = {
  offers: Offer[]
  total: number
  has_more: boolean
}

type AcceptOfferResponse = {
  offer: Offer
  deal: import('../deals/API').Deal
}
```
