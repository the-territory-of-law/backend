# Users API

CRUD пользователей.

Статус: **реализовано** (роутер подключён в приложении).

Маршруты без общего префикса: `/users`, `/users/{user_id}`.

Для регистрации с выдачей cookie предпочтительнее `POST /auth/register`.

---

## Создать пользователя

```http
POST /users
```

### Тело запроса

```json
{
  "name": "Алексей Смирнов",
  "email": "lawyer@example.com",
  "password": "securePassword123",
  "role": "lawyer"
}
```

### Ответ `200`

```json
{
  "id": 10,
  "email": "lawyer@example.com",
  "username": "Алексей Смирнов",
  "role": "lawyer"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Email уже существует |
| `422` | Валидация не пройдена |

---

## Получить пользователя

```http
GET /users/{user_id}
```

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `user_id` | `integer` | ID пользователя |

### Ответ `200`

```json
{
  "id": 10,
  "email": "lawyer@example.com",
  "username": "Алексей Смирнов",
  "role": "lawyer"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `404` | Пользователь не найден |

---

## Список пользователей

```http
GET /users
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `page` | `integer` | Номер страницы (с `1`) |
| `size` | `integer` | Размер страницы (`1`–`100`) |

Пагинация через `get_pagination_params`: `limit` = `size`, `offset` = `(page - 1) * size`.

### Ответ `200`

```json
[
  {
    "id": 10,
    "email": "lawyer@example.com",
    "username": "Алексей Смирнов",
    "role": "lawyer"
  },
  {
    "id": 20,
    "email": "ivan@example.com",
    "username": "Иван Петров",
    "role": "client"
  }
]
```

### Ошибки

| Код | Описание |
|---|---|
| `422` | Некорректные `page` / `size` |

---

## Обновить пользователя

```http
PATCH /users/{user_id}
```

### Тело запроса

Все поля опциональны.

```json
{
  "name": "Алексей Смирнов (обновлён)",
  "email": "newemail@example.com",
  "password": "newPassword456",
  "role": "lawyer"
}
```

### Ответ `200`

```json
{
  "id": 10,
  "email": "newemail@example.com",
  "username": "Алексей Смирнов (обновлён)",
  "role": "lawyer"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `404` | Пользователь не найден |
| `422` | Валидация не пройдена |

---

## Удалить пользователя

```http
DELETE /users/{user_id}
```

### Ответ `200`

```json
true
```

### Ошибки

| Код | Описание |
|---|---|
| `404` | Пользователь не найден |

---

# Структуры данных

```ts
type UserRole = 'client' | 'lawyer' | 'admin'

type UserResponse = {
  id: number
  email: string
  username: string
  role: UserRole
}

type UserCreate = {
  name: string
  email: string
  password: string
  role: UserRole
}

type UserUpdate = {
  name?: string
  email?: string
  password?: string
  role?: UserRole
}
```
