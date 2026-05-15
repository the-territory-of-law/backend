# Auth API

Документация по аутентификации. Cookie-based JWT.

Статус: **реализовано** (`/auth` подключён в приложении).

Базовый префикс: `/auth`.

После успешного `login` / `register` в ответе выставляются HttpOnly cookie:

| Cookie | Назначение |
|---|---|
| `access_token` | Access JWT (имя из `COOKIE_NAME`) |
| `refresh_token` | Refresh JWT |

Для REST и WebSocket чата используйте `credentials: 'include'` или `?token=<access_jwt>`.

---

## Регистрация

```http
POST /auth/register
```

### Тело запроса

`Content-Type: application/json`

```json
{
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "password": "securePassword123",
  "role": "client"
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `name` | `string` | Да | Отображаемое имя (в БД — `username`) |
| `email` | `string` | Да | Email (уникальный) |
| `password` | `string` | Да | Пароль |
| `role` | `string` | Да | `client`, `lawyer` или `admin` |

### Ответ `200`

```json
{
  "message": "Registered successfully",
  "user": {
    "id": 20,
    "email": "ivan@example.com",
    "username": "Иван Петров",
    "role": "client"
  }
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Email уже занят |
| `422` | Невалидное тело (email, role и т.д.) |

---

## Вход

```http
POST /auth/login
```

### Тело запроса

`Content-Type: application/x-www-form-urlencoded`

| Поле | Описание |
|---|---|
| `username` | **Email** пользователя (не логин) |
| `password` | Пароль |

### Ответ `200`

```json
{
  "message": "Logged in successfully"
}
```

В ответе — Set-Cookie с access и refresh токенами.

### Ошибки

| Код | Описание |
|---|---|
| `401` | `Invalid credentials` — неверный email или пароль |
| `422` | Не переданы `username` / `password` |

---

## Обновить access token

```http
POST /auth/refresh
```

Требует cookie `refresh_token`.

### Ответ `200`

```json
{
  "message": "Token refreshed"
}
```

Обновляется cookie `access_token`.

### Ошибки

| Код | Описание |
|---|---|
| `401` | `No refresh token` |
| `401` | `Invalid refresh token` |

---

## Выход

```http
POST /auth/logout
```

Требует валидный access token (cookie).

### Ответ `200`

```json
{
  "message": "Logged out"
}
```

Очищает auth cookies.

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |

---

# Структуры данных

```ts
type UserRole = 'client' | 'lawyer' | 'admin'

type UserCreate = {
  name: string
  email: string
  password: string
  role: UserRole
}

type UserPublic = {
  id: number
  email: string
  username: string
  role: UserRole
}
```
