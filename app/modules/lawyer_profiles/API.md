# Lawyer Profiles API

Документация по профилям юристов и верификации диплома.

Статус: **предлагаемый API (draft, HTTP ещё не реализован)**.

Базовый префикс: `/lawyer-profiles`.

Админ-эндпоинты верификации: префикс `/admin` (см. [Admin API](../admin/API.md)).

## Статусы верификации

| Значение | Описание |
|---|---|
| `pending` | Диплом на проверке, профиль не в публичном поиске |
| `approved` | Проверен, профиль доступен |
| `rejected` | Отклонён |

---

## Создать профиль

```http
POST /lawyer-profiles
```

### Тело запроса

```json
{
  "user_id": 10,
  "city": "Москва",
  "about": "Юрист по семейным делам, 8 лет практики",
  "experience_years": 8,
  "practice_area_ids": [1, 2]
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `user_id` | `integer` | Да | ID пользователя с ролью `lawyer` |
| `city` | `string` | Нет | Город |
| `about` | `string` | Нет | О себе |
| `experience_years` | `integer` | Нет | Стаж |
| `practice_area_ids` | `integer[]` | Нет | ID областей практики |

### Ответ `201`

```json
{
  "id": 3,
  "user_id": 10,
  "city": "Москва",
  "about": "Юрист по семейным делам, 8 лет практики",
  "experience_years": 8,
  "verification_status": "pending",
  "practice_areas": [
    { "id": 1, "name": "Семейное право" },
    { "id": 2, "name": "Раздел имущества" }
  ]
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Профиль для user_id уже существует |
| `401` | Не авторизован |
| `403` | Нет прав |
| `404` | Пользователь не найден |
| `422` | Валидация |

---

## Загрузить диплом

```http
POST /lawyer-profiles/{profile_id}/diploma
```

### Тело запроса

`multipart/form-data`

| Поле | Тип | Обязательное |
|---|---|---|
| `file` | `file` | Да |

### Ответ `201`

```json
{
  "diploma_file_id": 901,
  "verification_status": "pending"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Не владелец профиля |
| `404` | Профиль не найден |
| `413` | Файл слишком большой |

---

## Получить профиль

```http
GET /lawyer-profiles/{profile_id}
```

### Ответ `200`

```json
{
  "id": 3,
  "user_id": 10,
  "city": "Москва",
  "about": "Юрист по семейным делам, 8 лет практики",
  "experience_years": 8,
  "verification_status": "approved",
  "practice_areas": [
    { "id": 1, "name": "Семейное право" }
  ],
  "rating_avg": 4.8,
  "reviews_count": 24
}
```

### Ошибки

| Код | Описание |
|---|---|
| `404` | Профиль не найден |

---

## Список профилей

```http
GET /lawyer-profiles
```

По умолчанию только `verification_status` = `approved`.

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `practice_area_id` | `integer` | Область практики |
| `city` | `string` | Город |
| `experience_years_gte` | `integer` | Минимальный стаж |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "profiles": [
    {
      "id": 3,
      "user_id": 10,
      "city": "Москва",
      "about": "Юрист по семейным делам",
      "experience_years": 8,
      "verification_status": "approved",
      "practice_areas": [{ "id": 1, "name": "Семейное право" }],
      "rating_avg": 4.8,
      "reviews_count": 24
    }
  ],
  "total": 15,
  "has_more": true
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Некорректные фильтры |

---

## Обновить профиль

```http
PATCH /lawyer-profiles/{profile_id}
```

### Тело запроса

```json
{
  "city": "Санкт-Петербург",
  "about": "Обновлённое описание",
  "experience_years": 9
}
```

### Ответ `200`

Объект профиля (как в `GET`).

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Не владелец |
| `404` | Не найден |
| `422` | Валидация |

---

## Статус верификации

```http
GET /lawyer-profiles/{profile_id}/verification
```

### Ответ `200`

```json
{
  "status": "pending",
  "comment": null,
  "reviewed_by": null,
  "reviewed_at": null
}
```

```json
{
  "status": "rejected",
  "comment": "Документ нечитаем, загрузите скан лучшего качества",
  "reviewed_by": 1,
  "reviewed_at": "2026-05-11T09:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа |
| `404` | Профиль не найден |

---

# Структуры данных

```ts
type VerificationStatus = 'pending' | 'approved' | 'rejected'

type PracticeArea = {
  id: number
  name: string
}

type LawyerProfile = {
  id: number
  user_id: number
  city: string | null
  about: string | null
  experience_years: number | null
  verification_status: VerificationStatus
  practice_areas: PracticeArea[]
  rating_avg?: number
  reviews_count?: number
}

type LawyerProfilesPage = {
  profiles: LawyerProfile[]
  total: number
  has_more: boolean
}

type VerificationInfo = {
  status: VerificationStatus
  comment: string | null
  reviewed_by: number | null
  reviewed_at: string | null
}
```
