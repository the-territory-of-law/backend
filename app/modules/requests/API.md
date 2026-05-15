# Requests API

Документация по заявкам клиентов.

Статус: **предлагаемый API (draft, HTTP ещё не реализован)**.

Базовый префикс: `/requests`.

## Статусы заявки

| Значение | Описание |
|---|---|
| `open` | Принимаются офферы |
| `closed` | Заявка закрыта |

## Категории (пример из модели)

| Значение | Описание |
|---|---|
| `devorce` | Семейное / развод |
| `shishka` | Другое направление (как в БД) |

---

## Создать заявку

```http
POST /requests
```

Только для роли `client`.

### Тело запроса

```json
{
  "title": "Развод и раздел имущества",
  "description": "Нужна консультация и представительство в суде",
  "category": "devorce",
  "budget": "big",
  "budget_value": 100000
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `title` | `string` | Да | Заголовок |
| `description` | `string` | Да | Описание |
| `category` | `string` | Нет | `devorce`, `shishka` |
| `budget` | `string` | Нет | `big`, `bomsh` |
| `budget_value` | `integer` | Нет | Числовой бюджет |

### Ответ `201`

```json
{
  "id": 40,
  "client_id": 20,
  "title": "Развод и раздел имущества",
  "description": "Нужна консультация и представительство в суде",
  "category": "devorce",
  "budget": "big",
  "budget_value": 100000,
  "status": "open",
  "created_at": "2026-05-10T10:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Только клиент может создавать заявку |
| `422` | Валидация не пройдена |

---

## Получить заявку

```http
GET /requests/{request_id}
```

### Ответ `200`

```json
{
  "id": 40,
  "client_id": 20,
  "title": "Развод и раздел имущества",
  "description": "Нужна консультация и представительство в суде",
  "category": "devorce",
  "budget": "big",
  "budget_value": 100000,
  "status": "open",
  "created_at": "2026-05-10T10:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа к заявке |
| `404` | Заявка не найдена |

---

## Список заявок

```http
GET /requests
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `status` | `string` | `open`, `closed` |
| `category` | `string` | Категория |
| `budget_min` | `integer` | Минимум `budget_value` |
| `budget_max` | `integer` | Максимум `budget_value` |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "requests": [
    {
      "id": 40,
      "client_id": 20,
      "title": "Развод и раздел имущества",
      "description": "Нужна консультация",
      "category": "devorce",
      "budget": "big",
      "budget_value": 100000,
      "status": "open",
      "created_at": "2026-05-10T10:00:00Z"
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
| `400` | Некорректные фильтры |

---

## Обновить заявку

```http
PATCH /requests/{request_id}
```

Только владелец (клиент), пока `status` = `open`.

### Тело запроса

```json
{
  "title": "Развод — уточнение",
  "description": "Обновлённое описание",
  "budget_value": 120000
}
```

### Ответ `200`

Объект заявки (как в `GET /requests/{request_id}`).

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Не владелец или заявка закрыта |
| `404` | Не найдена |
| `422` | Валидация |

---

## Закрыть заявку

```http
POST /requests/{request_id}/close
```

### Тело запроса

```json
{
  "reason": "Выбран юрист, сделка создана"
}
```

| Поле | Тип | Обязательное |
|---|---|---|
| `reason` | `string` | Нет |

### Ответ `200`

```json
{
  "id": 40,
  "client_id": 20,
  "title": "Развод и раздел имущества",
  "description": "Нужна консультация",
  "category": "devorce",
  "budget": "big",
  "budget_value": 100000,
  "status": "closed",
  "created_at": "2026-05-10T10:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Заявка уже закрыта |
| `401` | Не авторизован |
| `403` | Не владелец |
| `404` | Не найдена |

---

# Структуры данных

```ts
type Request = {
  id: number
  client_id: number
  title: string
  description: string | null
  category: string
  budget: string
  budget_value: number | null
  status: 'open' | 'closed'
  created_at: string
}

type RequestsPage = {
  requests: Request[]
  total: number
  has_more: boolean
}
```
