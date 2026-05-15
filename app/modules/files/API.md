# Files API

Документация по загрузке и выдаче файлов.

Статус: **частично реализовано** — вложения чата: `POST /chats/{deal_id}/attachments` (см. [Chat API](../chat/API.md)).

Общий модуль `/files` — **draft**, HTTP ещё не реализован.

Базовый префикс: `/files`.

---

## Загрузить файл (общий)

```http
POST /files/upload
```

### Тело запроса

`multipart/form-data`

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `file` | `file` | Да | Файл |
| `entity_type` | `string` | Да | `dispute`, `request`, `profile`, … |
| `entity_id` | `integer` | Да | ID сущности |

### Ответ `201`

```json
{
  "id": 801,
  "url": "/static/files/801_contract.pdf",
  "filename": "contract.pdf",
  "mime_type": "application/pdf",
  "size": 512000,
  "entity_type": "dispute",
  "entity_id": 7
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет прав на сущность |
| `413` | Файл слишком большой |
| `422` | Неподдерживаемый тип |

---

## Загрузить вложение для чата

```http
POST /files/chat-upload
```

> Реализованный аналог: `POST /chats/{deal_id}/attachments`.

### Тело запроса

`multipart/form-data`

| Поле | Тип | Обязательное |
|---|---|---|
| `file` | `file` | Да |
| `deal_id` | `integer` | Да |

### Ответ `201`

```json
{
  "file_id": 305,
  "deal_id": 201,
  "url": "/static/chat/201/a1b2_evidence.jpg",
  "mime_type": "image/jpeg",
  "size": 245760
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Не участник сделки |
| `404` | Сделка не найдена |
| `413` | Превышен лимит размера |

---

## Метаданные файла

```http
GET /files/{file_id}
```

### Ответ `200`

```json
{
  "id": 801,
  "url": "/static/files/801_contract.pdf",
  "filename": "contract.pdf",
  "mime_type": "application/pdf",
  "size": 512000,
  "entity_type": "dispute",
  "entity_id": 7,
  "created_at": "2026-05-12T12:00:00Z"
}
```

### Ошибки

| Код | Описание |
|---|---|
| `401` | Не авторизован |
| `403` | Нет доступа |
| `404` | Файл не найден |

---

## Скачать файл

```http
GET /files/{file_id}/download
```

### Ответ `200`

Бинарное тело, заголовки:

| Заголовок | Пример |
|---|---|
| `Content-Type` | `application/pdf` |
| `Content-Disposition` | `attachment; filename="contract.pdf"` |

### Ошибки

| Код | Описание |
|---|---|
| `403` | Нет доступа |
| `404` | Не найден |

---

## Список файлов сущности

```http
GET /files
```

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `entity_type` | `string` | Тип сущности |
| `entity_id` | `integer` | ID сущности |
| `limit` | `integer` | Лимит |
| `offset` | `integer` | Смещение |

### Ответ `200`

```json
{
  "files": [
    {
      "id": 801,
      "url": "/static/files/801_contract.pdf",
      "filename": "contract.pdf",
      "mime_type": "application/pdf",
      "size": 512000
    }
  ],
  "total": 1,
  "has_more": false
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Не переданы `entity_type` / `entity_id` |

---

## Привязать файл к сообщению

```http
POST /files/{file_id}/attach-to-message
```

> В чате предпочтительно: предзагрузка + `attachment_ids` в `POST /chats/{deal_id}/messages` или WS.

### Тело запроса

```json
{
  "message_id": 1010
}
```

### Ответ `200`

```json
{
  "message_id": 1010,
  "file_id": 801
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Файл уже привязан |
| `403` | Нет прав |
| `404` | Файл или сообщение не найдены |

---

## Удалить файл

```http
DELETE /files/{file_id}
```

### Ответ `204`

Пустое тело.

### Ошибки

| Код | Описание |
|---|---|
| `403` | Нет прав |
| `404` | Не найден |

---

# Структуры данных

```ts
type FileMeta = {
  id: number
  url: string
  filename: string
  mime_type: string
  size: number
  entity_type?: string
  entity_id?: number
  created_at?: string
}

type FilesPage = {
  files: FileMeta[]
  total: number
  has_more: boolean
}
```
