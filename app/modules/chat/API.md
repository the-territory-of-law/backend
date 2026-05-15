# Chat API

Документация по REST API и WebSocket для чатов между клиентом и юристом в рамках сделки.

## Общая модель

Чат привязан к сделке через `deal_id`.

Основные сущности:

- `chat` — чат по сделке;
- `message` — сообщение в чате;
- `attachment` — файл или изображение, прикреплённое к сообщению;
- `delivery_statuses` — статусы доставки/прочтения сообщения;
- `edit_history` — история изменений текстовой части сообщения.

## Главное правило сообщения

Сообщение — это контейнер.

Одно сообщение может содержать:

- только текст;
- только файл;
- только изображение;
- текст + файл;
- текст + изображение;
- текст + файл + изображение;
- несколько файлов и изображений одновременно.

Для этого у сообщения есть:

- `text` — текстовая часть сообщения;
- `attachments` — массив вложений.

Если вложений нет, `attachments` возвращается пустым массивом.

Если текста нет, `text` возвращается как `null`.

## Типы вложений

| Значение | Описание |
|---|---|
| `image` | Изображение |
| `file` | Обычный файл |

## Статусы доставки сообщения

| Значение | Описание |
|---|---|
| `sent` | Сообщение отправлено |
| `delivered` | Сообщение доставлено |
| `read` | Сообщение прочитано |
| `failed` | Сообщение не прошло модерацию (Ollama / эвристики) |

При создании сообщения для получателя создаётся статус `sent`. Если получатель **онлайн** в WS-чате этой сделки, статус сразу становится `delivered`. При открытии истории (`GET .../messages`) или подключении к WS все накопившиеся `sent` для пользователя в сделке переводятся в `delivered`. Статус `read` выставляется явно (см. прочтение ниже).

## Авторизация REST

Все REST-запросы требуют авторизованного пользователя. Используется cookie с access-токеном (как в остальных защищённых endpoint приложения).

---

# REST API

## Получить список чатов

```http
GET /chats
```

Возвращает список чатов текущего пользователя.

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `limit` | `integer` | Количество чатов |
| `offset` | `integer` | Смещение для пагинации |

### Ответ `200`

```json
[
  {
    "deal_id": 201,
    "client_id": 20,
    "client_name": "Иван Петров",
    "client_avatar_url": "https://storage.example.com/avatars/20.jpg",
    "lawyer_id": 10,
    "lawyer_name": "Алексей Смирнов",
    "lawyer_avatar_url": "https://storage.example.com/avatars/10.jpg",
    "deal_status": "active",
    "last_message": {
      "id": 1005,
      "text": "Документы готовы, проверьте",
      "sender_id": 10,
      "attachments": [
        {
          "id": 302,
          "type": "file",
          "filename": "contract.pdf",
          "mime": "application/pdf"
        }
      ],
      "created_at": "2026-05-10T14:30:00Z"
    },
    "unread_count": 2
  }
]
```

> Поля `client_avatar_url` и `lawyer_avatar_url` могут быть `null`, если аватар в профиле не задан или ещё не подключён к API.

---

## Получить историю сообщений

```http
GET /chats/{deal_id}/messages
```

Возвращает историю сообщений по сделке.

Сообщения идут от старых к новым.

Поле `edit_history` есть всегда.

Поле `attachments` есть всегда.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Query-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `limit` | `integer` | Количество сообщений |
| `offset` | `integer` | Смещение для пагинации |

### Ответ `200`

```json
{
  "messages": [
    {
      "id": 1001,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 20,
      "text": "Здравствуйте!",
      "attachments": [],
      "created_at": "2026-05-10T13:05:00Z",
      "edited_at": null,
      "deleted_at": null,
      "edit_history": [],
      "delivery_statuses": [
        {
          "user_id": 10,
          "status": "read",
          "at": "2026-05-10T13:06:00Z"
        }
      ]
    },
    {
      "id": 1002,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 10,
      "text": "Финальная версия",
      "attachments": [],
      "created_at": "2026-05-10T14:00:00Z",
      "edited_at": "2026-05-10T15:30:00Z",
      "deleted_at": null,
      "edit_history": [
        {
          "old_text": "Предпоследняя версия",
          "edited_at": "2026-05-10T15:30:00Z"
        },
        {
          "old_text": "Изначальный текст",
          "edited_at": "2026-05-10T15:15:00Z"
        }
      ],
      "delivery_statuses": [
        {
          "user_id": 20,
          "status": "read",
          "at": "2026-05-10T15:31:00Z"
        }
      ]
    },
    {
      "id": 1003,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 10,
      "text": "Вот фото документа",
      "attachments": [
        {
          "id": 301,
          "type": "image",
          "url": "https://storage.example.com/images/photo.jpg",
          "filename": "photo.jpg",
          "size": 245760,
          "mime": "image/jpeg",
          "width": 1920,
          "height": 1080,
          "thumbnail_url": "https://storage.example.com/images/photo_thumb.jpg"
        }
      ],
      "created_at": "2026-05-10T14:10:00Z",
      "edited_at": null,
      "deleted_at": null,
      "edit_history": [],
      "delivery_statuses": [
        {
          "user_id": 20,
          "status": "delivered",
          "at": "2026-05-10T14:10:00Z"
        }
      ]
    },
    {
      "id": 1004,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 10,
      "text": "Прикрепляю договор",
      "attachments": [
        {
          "id": 302,
          "type": "file",
          "url": "https://storage.example.com/files/contract.pdf",
          "filename": "contract.pdf",
          "size": 512000,
          "mime": "application/pdf"
        }
      ],
      "created_at": "2026-05-10T14:15:00Z",
      "edited_at": null,
      "deleted_at": null,
      "edit_history": [],
      "delivery_statuses": [
        {
          "user_id": 20,
          "status": "read",
          "at": "2026-05-10T14:20:00Z"
        }
      ]
    },
    {
      "id": 1005,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 20,
      "text": "Вот фото и файл по делу",
      "attachments": [
        {
          "id": 303,
          "type": "image",
          "url": "https://storage.example.com/images/evidence.jpg",
          "filename": "evidence.jpg",
          "size": 245760,
          "mime": "image/jpeg",
          "width": 1920,
          "height": 1080,
          "thumbnail_url": "https://storage.example.com/images/evidence_thumb.jpg"
        },
        {
          "id": 304,
          "type": "file",
          "url": "https://storage.example.com/files/contract.pdf",
          "filename": "contract.pdf",
          "size": 512000,
          "mime": "application/pdf"
        }
      ],
      "created_at": "2026-05-10T14:30:00Z",
      "edited_at": null,
      "deleted_at": null,
      "edit_history": [],
      "delivery_statuses": [
        {
          "user_id": 10,
          "status": "read",
          "at": "2026-05-10T14:31:00Z"
        }
      ]
    },
    {
      "id": 1006,
      "deal_id": 201,
      "client_id": 20,
      "sender_id": 20,
      "text": "Сообщение удалено",
      "attachments": [],
      "created_at": "2026-05-10T14:35:00Z",
      "edited_at": null,
      "deleted_at": "2026-05-10T15:00:00Z",
      "edit_history": [],
      "delivery_statuses": [
        {
          "user_id": 10,
          "status": "read",
          "at": "2026-05-10T14:36:00Z"
        }
      ]
    }
  ],
  "total": 42,
  "has_more": true
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Пользователь не является участником сделки |
| `404` | Сделка не найдена |

---

## Загрузить вложение (предзагрузка)

```http
POST /chats/{deal_id}/attachments
```

Загружает файл или изображение **без привязки к сообщению**. После загрузки возвращается `file_id` — его передают в `POST /chats/{deal_id}/messages` (JSON) или в WebSocket `message.data.attachment_ids`.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Тело запроса

```http
multipart/form-data
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `file` | `file` | Да | Файл или изображение |

### Ответ `201`

```json
{
  "file_id": 305,
  "url": "/uploads/chat/201/a1b2_evidence.jpg",
  "mime_type": "image/jpeg",
  "size": 245760
}
```

### Ошибки

| Код | Описание |
|---|---|
| `403` | Пользователь не является участником сделки |
| `404` | Сделка не найдена |
| `413` | Файл слишком большой |

---

## Прочитать все сообщения до указанного id

```http
POST /chats/{deal_id}/read-through
```

Помечает **прочитанными** все **входящие** сообщения сделки (не от текущего пользователя, не удалённые) с `id ≤ message_id`. Удобно при открытии чата или прокрутке до последнего видимого сообщения.

Собственные сообщения этим запросом не помечаются.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Тело запроса

```json
{
  "message_id": 1005
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `message_id` | `integer` | Да | ID последнего прочитанного сообщения (watermark) |

### Ответ `200`

```json
{
  "through_message_id": 1005,
  "marked_message_ids": [1001, 1002, 1003, 1004],
  "read_at": "2026-05-10T16:30:00Z"
}
```

| Поле | Описание |
|---|---|
| `through_message_id` | Переданный watermark |
| `marked_message_ids` | ID сообщений, для которых статус реально изменился на `read` в этом запросе |
| `read_at` | Время прочтения |

После успеха бэкенд рассылает участникам сделки WebSocket-событие `read_through` (см. ниже).

### Ошибки

| Код | Описание |
|---|---|
| `400` | Сообщение не принадлежит этой сделке |
| `403` | Пользователь не является участником сделки |
| `404` | Сообщение или сделка не найдены |

---

## Отправить сообщение

```http
POST /chats/{deal_id}/messages
```

Создаёт новое сообщение в чате.

Сообщение может содержать текст и несколько вложений одновременно.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Тело запроса

Поддерживаются два формата.

#### Вариант 1: `multipart/form-data` (файлы в том же запросе)

```http
multipart/form-data
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `text` | `string` | Нет | Текст сообщения |
| `attachments[]` | `file[]` | Нет | Один или несколько файлов/изображений (допускается также имя поля `attachments`) |

#### Вариант 2: `application/json` (предзагруженные вложения)

```json
{
  "text": "Вот договор",
  "attachments": [305, 306]
}
```

| Поле | Тип | Обязательное | Описание |
|---|---|---|---|
| `text` | `string` | Нет | Текст сообщения |
| `attachments` | `integer[]` | Нет | ID файлов после `POST /chats/{deal_id}/attachments` |

После успешного создания сообщения (любым способом) бэкенд рассылает WebSocket-событие `new_message`.

### Правила валидации

- Должно быть заполнено хотя бы одно поле: `text` или `attachments[]`.
- Если отправляется только текст, `attachments[]` можно не передавать.
- Если отправляются только файлы, `text` можно не передавать.
- Если отправляются текст и файлы, они создают одно сообщение.
- Тип вложения определяется по MIME-типу файла:
  - `image/*` → `image`;
  - всё остальное → `file`.

### Пример запроса: текст + изображение + файл

```http
POST /chats/201/messages
Content-Type: multipart/form-data

text=Вот фото и договор по делу
attachments[]=evidence.jpg
attachments[]=contract.pdf
```

### Ответ `201` — текстовое сообщение без вложений

```json
{
  "id": 1007,
  "deal_id": 201,
  "client_id": 20,
  "sender_id": 20,
  "text": "Текст сообщения",
  "attachments": [],
  "created_at": "2026-05-10T16:00:00Z",
  "edited_at": null,
  "deleted_at": null,
  "edit_history": [],
  "delivery_statuses": [
    {
      "user_id": 10,
      "status": "sent",
      "at": "2026-05-10T16:00:00Z"
    }
  ]
}
```

### Ответ `201` — сообщение с изображением

```json
{
  "id": 1008,
  "deal_id": 201,
  "client_id": 20,
  "sender_id": 20,
  "text": "Вот фото документа",
  "attachments": [
    {
      "id": 303,
      "type": "image",
      "url": "https://storage.example.com/images/photo.jpg",
      "filename": "photo.jpg",
      "size": 245760,
      "mime": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "thumbnail_url": "https://storage.example.com/images/photo_thumb.jpg"
    }
  ],
  "created_at": "2026-05-10T16:05:00Z",
  "edited_at": null,
  "deleted_at": null,
  "edit_history": [],
  "delivery_statuses": [
    {
      "user_id": 10,
      "status": "sent",
      "at": "2026-05-10T16:05:00Z"
    }
  ]
}
```

### Ответ `201` — сообщение с файлом

```json
{
  "id": 1009,
  "deal_id": 201,
  "client_id": 20,
  "sender_id": 20,
  "text": "Прикрепляю договор",
  "attachments": [
    {
      "id": 304,
      "type": "file",
      "url": "https://storage.example.com/files/contract.pdf",
      "filename": "contract.pdf",
      "size": 512000,
      "mime": "application/pdf"
    }
  ],
  "created_at": "2026-05-10T16:10:00Z",
  "edited_at": null,
  "deleted_at": null,
  "edit_history": [],
  "delivery_statuses": [
    {
      "user_id": 10,
      "status": "sent",
      "at": "2026-05-10T16:10:00Z"
    }
  ]
}
```

### Ответ `201` — сообщение с текстом, изображением и файлом

```json
{
  "id": 1010,
  "deal_id": 201,
  "client_id": 20,
  "sender_id": 20,
  "text": "Вот фото и договор по делу",
  "attachments": [
    {
      "id": 305,
      "type": "image",
      "url": "https://storage.example.com/images/evidence.jpg",
      "filename": "evidence.jpg",
      "size": 245760,
      "mime": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "thumbnail_url": "https://storage.example.com/images/evidence_thumb.jpg"
    },
    {
      "id": 306,
      "type": "file",
      "url": "https://storage.example.com/files/contract.pdf",
      "filename": "contract.pdf",
      "size": 512000,
      "mime": "application/pdf"
    }
  ],
  "created_at": "2026-05-10T16:15:00Z",
  "edited_at": null,
  "deleted_at": null,
  "edit_history": [],
  "delivery_statuses": [
    {
      "user_id": 10,
      "status": "sent",
      "at": "2026-05-10T16:15:00Z"
    }
  ]
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Пустой `text` и нет вложений / неверные `attachment` id |
| `400` | Некорректный JSON |
| `403` | Пользователь не является участником сделки |
| `404` | Сделка не найдена |
| `413` | Один или несколько файлов слишком большие |
| `422` | Текст не прошёл модерацию (`message_failed`) |

### Ошибка `422` — модерация (не прошло валидацию)

Сообщение **сохраняется** у отправителя: в истории видно только ему, в `delivery_statuses` у отправителя статус `failed`, поле `blocked_reason` с причиной. Собеседнику не доставляется.

```json
{
  "detail": {
    "code": "message_failed",
    "status": "failed",
    "reason": "Упоминание стороннего мессенджера или канала связи.",
    "blocked_reason": "Упоминание стороннего мессенджера или канала связи.",
    "message": {
      "id": 1011,
      "deal_id": 201,
      "sender_id": 20,
      "text": "напиши в телеграм",
      "blocked_reason": "Упоминание стороннего мессенджера или канала связи.",
      "delivery_statuses": [
        {
          "user_id": 20,
          "status": "failed",
          "at": "2026-05-10T16:00:00Z"
        }
      ]
    }
  }
}
```

Проверка: сначала **Ollama** (`OFF_PLATFORM_OLLAMA_ENABLED`, `OLLAMA_BASE_URL`), затем эвристики, если модель пропустила или недоступна.

---

## Изменить сообщение

```http
PATCH /chats/messages/{message_id}
```

Изменяет текстовую часть своего сообщения.

Можно изменить текст как у обычного текстового сообщения, так и у сообщения с вложениями.

Вложения через этот endpoint не редактируются.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `message_id` | `integer` | ID сообщения |

### Тело запроса

```json
{
  "text": "Исправленный текст"
}
```

### Ответ `200`

```json
{
  "id": 1010,
  "deal_id": 201,
  "client_id": 20,
  "sender_id": 20,
  "text": "Исправленный текст",
  "attachments": [
    {
      "id": 305,
      "type": "image",
      "url": "https://storage.example.com/images/evidence.jpg",
      "filename": "evidence.jpg",
      "size": 245760,
      "mime": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "thumbnail_url": "https://storage.example.com/images/evidence_thumb.jpg"
    },
    {
      "id": 306,
      "type": "file",
      "url": "https://storage.example.com/files/contract.pdf",
      "filename": "contract.pdf",
      "size": 512000,
      "mime": "application/pdf"
    }
  ],
  "edited_at": "2026-05-10T16:20:00Z",
  "deleted_at": null,
  "edit_history": [
    {
      "old_text": "Вот фото и договор по делу",
      "edited_at": "2026-05-10T16:20:00Z"
    }
  ],
  "delivery_statuses": [
    {
      "user_id": 10,
      "status": "read",
      "at": "2026-05-10T16:18:00Z"
    }
  ]
}
```

### Ошибки

| Код | Описание |
|---|---|
| `400` | Пустой текст |
| `403` | Пользователь не является автором сообщения |
| `404` | Сообщение не найдено |
| `422` | Новый текст не прошёл модерацию (`message_failed`, без сохранения правки) |

После успешного изменения бэкенд рассылает WebSocket-событие `message_updated`.

---

## Удалить сообщение

```http
DELETE /chats/messages/{message_id}
```

Удаляет своё сообщение.

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `message_id` | `integer` | ID сообщения |

### Ответ `204`

Пустое тело ответа.

### Ошибки

| Код | Описание |
|---|---|
| `403` | Пользователь не является автором сообщения |
| `404` | Сообщение не найдено |

После успешного удаления бэкенд рассылает WebSocket-событие `message_deleted`.

---

# WebSocket API

## Подключение

```http
WS /ws/deals/{deal_id}/chat
```

Локальные примеры:

```text
ws://localhost:8000/ws/deals/201/chat?token=<access_jwt>
```

В браузере можно подключаться **без** query-параметра, если access-токен уже в cookie (то же имя cookie, что и для REST).

### Path-параметры

| Параметр | Тип | Описание |
|---|---|---|
| `deal_id` | `integer` | ID сделки |

### Авторизация

| Способ | Описание |
|---|---|
| Query `token` | Access JWT (тип `access` в payload) |
| Cookie | Access-токен в cookie авторизации (как для REST) |

При ошибке авторизации соединение закрывается с кодом `4001` (не авторизован) или `4003` (нет доступа к сделке).

### Query-параметры (опционально)

| Параметр | Тип | Описание |
|---|---|---|
| `token` | `string` | Access JWT, если cookie недоступны (например, нативный клиент) |

---

## Служебные кадры

### Ping (клиент → сервер)

```json
{
  "type": "ping"
}
```

### Pong (сервер → клиент)

```json
{
  "type": "pong"
}
```

---

## События от фронта к бэку

### Отправить текстовое сообщение

```json
{
  "type": "message",
  "data": {
    "text": "Привет",
    "attachment_ids": []
  }
}
```

### Отправить сообщение с уже загруженными вложениями

Если сообщение отправляется через WebSocket, файлы должны быть предварительно загружены отдельным REST endpoint для загрузки файлов.

После загрузки файлов фронт отправляет через WebSocket только их ID.

```json
{
  "type": "message",
  "data": {
    "text": "Вот фото и договор по делу",
    "attachment_ids": [305, 306]
  }
}
```

> Если отдельного endpoint для предварительной загрузки файлов нет, сообщения с файлами нужно создавать через `POST /chats/{deal_id}/messages`.
> После создания сообщения бэк должен разослать событие `new_message` через WebSocket.

### Отметить одно сообщение прочитанным

Помечает **одно** сообщение по `message_id` (в отличие от `read_through`).

```json
{
  "type": "read",
  "message_id": 1004
}
```

Участники получают событие `status` с `status: "read"`.

### Прочитать все входящие до указанного id

Аналог `POST /chats/{deal_id}/read-through`.

```json
{
  "type": "read_through",
  "message_id": 1005
}
```

Участники получают событие `read_through` (см. ниже).

### Пользователь печатает

```json
{
  "type": "typing"
}
```

### Пользователь перестал печатать

```json
{
  "type": "stop_typing"
}
```

---

## События от бэка к фронту

### Новое сообщение

```json
{
  "type": "new_message",
  "message": {
    "id": 1010,
    "deal_id": 201,
    "client_id": 20,
    "sender_id": 20,
    "text": "Вот фото и договор по делу",
    "attachments": [
      {
        "id": 305,
        "type": "image",
        "url": "https://storage.example.com/images/evidence.jpg",
        "filename": "evidence.jpg",
        "size": 245760,
        "mime": "image/jpeg",
        "width": 1920,
        "height": 1080,
        "thumbnail_url": "https://storage.example.com/images/evidence_thumb.jpg"
      },
      {
        "id": 306,
        "type": "file",
        "url": "https://storage.example.com/files/contract.pdf",
        "filename": "contract.pdf",
        "size": 512000,
        "mime": "application/pdf"
      }
    ],
    "created_at": "2026-05-10T16:15:00Z",
    "edited_at": null,
    "deleted_at": null,
    "edit_history": [],
    "delivery_statuses": [
      {
        "user_id": 10,
        "status": "sent",
        "at": "2026-05-10T16:15:00Z"
      }
    ]
  }
}
```

### Сообщение отредактировано

```json
{
  "type": "message_updated",
  "message_id": 1010,
  "text": "Исправленный текст",
  "edited_at": "2026-05-10T16:20:00Z",
  "edit_history": [
    {
      "old_text": "Вот фото и договор по делу",
      "edited_at": "2026-05-10T16:20:00Z"
    }
  ]
}
```

### Сообщение удалено

```json
{
  "type": "message_deleted",
  "message_id": 1010,
  "deleted_at": "2026-05-10T16:25:00Z"
}
```

### Статус одного сообщения изменился

Событие после `read` (одно сообщение).

```json
{
  "type": "status",
  "message_id": 1010,
  "user_id": 10,
  "status": "read",
  "at": "2026-05-10T16:30:00Z"
}
```

### Пакетное прочтение (read through)

Событие после `read_through` (REST или WS).

```json
{
  "type": "read_through",
  "through_message_id": 1005,
  "user_id": 20,
  "message_ids": [1001, 1002, 1003, 1004],
  "at": "2026-05-10T16:30:00Z"
}
```

| Поле | Описание |
|---|---|
| `through_message_id` | Watermark (переданный `message_id`) |
| `user_id` | Кто прочитал |
| `message_ids` | Сообщения, помеченные `read` в этом действии |
| `at` | Время прочтения |

### Собеседник печатает

```json
{
  "type": "typing",
  "user_id": 10
}
```

### Собеседник перестал печатать

```json
{
  "type": "stop_typing",
  "user_id": 10
}
```

### Ошибка обработки

```json
{
  "type": "error",
  "message": "Текст пустой и вложения не переданы"
}
```

При блокировке модерации (отправка текста):

```json
{
  "type": "error",
  "code": "message_failed",
  "status": "failed",
  "reason": "Упоминание стороннего мессенджера или канала связи.",
  "blocked_reason": "Упоминание стороннего мессенджера или канала связи.",
  "message": { }
}
```

Дополнительно только отправителю:

```json
{
  "type": "message_failed",
  "status": "failed",
  "reason": "Упоминание стороннего мессенджера или канала связи.",
  "blocked_reason": "Упоминание стороннего мессенджера или канала связи.",
  "message": { }
}
```

Для невалидного JSON:

```json
{
  "type": "error",
  "detail": "invalid_json",
  "message": "invalid_json"
}
```

---

# Структуры данных

## Chat

```ts
type Chat = {
  deal_id: number
  client_id: number
  client_name: string
  client_avatar_url: string | null
  lawyer_id: number
  lawyer_name: string
  lawyer_avatar_url: string | null
  deal_status: string
  last_message: LastMessage | null
  unread_count: number
}
```

## LastMessage

```ts
type LastMessage = {
  id: number
  text: string | null
  sender_id: number
  attachments: LastMessageAttachment[]
  created_at: string
}
```

## LastMessageAttachment

```ts
type LastMessageAttachment = {
  id: number
  type: 'image' | 'file'
  filename: string
  mime: string
}
```

## Message

```ts
type Message = {
  id: number
  deal_id: number
  client_id: number
  sender_id: number
  text: string | null
  attachments: MessageAttachment[]
  created_at: string
  edited_at: string | null
  deleted_at: string | null
  edit_history: EditHistoryItem[]
  delivery_statuses: MessageDeliveryStatus[]
}
```

## MessageAttachment

```ts
type MessageAttachment = {
  id: number
  type: 'image' | 'file'
  url: string
  filename: string
  size: number
  mime: string
  width?: number
  height?: number
  thumbnail_url?: string
}
```

## EditHistoryItem

```ts
type EditHistoryItem = {
  old_text: string | null
  edited_at: string
}
```

## MessageDeliveryStatus

```ts
type MessageDeliveryStatus = {
  user_id: number
  status: 'sent' | 'delivered' | 'read' | 'failed'
  at: string
}
```

## ReadThroughResponse

```ts
type ReadThroughResponse = {
  through_message_id: number
  marked_message_ids: number[]
  read_at: string
}
```

## AttachmentUploadResponse

```ts
type AttachmentUploadResponse = {
  file_id: number
  url: string
  mime_type: string
  size: number
}
```

## MessagesPage

```ts
type MessagesPage = {
  messages: Message[]
  total: number
  has_more: boolean
}
```

---

# Важные правила

## Сообщение

- Сообщение больше не имеет поля `status` как типа контента.
- Тип есть у каждого вложения: `image` или `file`.
- Текст хранится отдельно в поле `text`.
- Вложения хранятся в массиве `attachments`.
- Одно сообщение может содержать и текст, и несколько вложений одновременно.

## История сообщений

- Сообщения возвращаются от старых к новым.
- Поле `edit_history` есть всегда.
- Поле `attachments` есть всегда.
- Если сообщение не редактировалось, `edit_history` будет пустым массивом.
- Если у сообщения нет вложений, `attachments` будет пустым массивом.
- Если у сообщения нет текста, `text` будет `null`.
- Если сообщение удалено, поле `deleted_at` содержит дату удаления.
- Удалённое сообщение может продолжать возвращаться в истории, но отображаться на фронте как удалённое.

## Отправка

- Можно отправить только текст.
- Можно отправить только файл.
- Можно отправить только изображение.
- Можно отправить текст + файл.
- Можно отправить текст + изображение.
- Можно отправить текст + файл + изображение.
- Можно отправить несколько файлов и изображений в одном сообщении.
- Нельзя отправить полностью пустое сообщение без текста и без вложений.

## Редактирование

- Редактировать можно только свои сообщения.
- Редактируется только поле `text`.
- Вложения через `PATCH /chats/messages/{message_id}` не редактируются.
- При редактировании старая версия текста попадает в `edit_history`.

## Удаление

- Удалить можно только своё сообщение.
- После удаления API возвращает `204`.
- Тело ответа пустое.

## Файлы и изображения

- Вложения всегда лежат в массиве `attachments`.
- У каждого вложения есть поле `type`.
- Если `type` равен `image`, у вложения могут быть дополнительные поля:
  - `width`;
  - `height`;
  - `thumbnail_url`.
- Если `type` равен `file`, вложение считается обычным файлом.
- Сейчас при загрузке `width`, `height` и `thumbnail_url` могут быть `null`, пока не включена генерация превью/размеров на бэкенде.

## Прочтение

- `read` — одно сообщение по `message_id`, событие `status`.
- `read_through` — все входящие с `id ≤ message_id`, событие `read_through`.
- Для сброса `unread_count` в списке чатов достаточно `read_through` по последнему видимому сообщению.
- REST: `POST /chats/{deal_id}/read-through`.
- WebSocket: `type: "read_through"`.

## Модерация текста (Ollama + эвристики)

- При **отправке** текста: Ollama (если включена) → эвристики; при блокировке — `422` / WS `error` + `message_failed`, сообщение у отправителя со статусом `failed`.
- При **редактировании**: та же проверка, но без сохранения нового текста — только `422`.
- Сообщения только с вложениями без текста модерация не затрагивает.
- Настройки: `OFF_PLATFORM_OLLAMA_ENABLED`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_REQUEST_TIMEOUT_SEC`.

## WebSocket

- WebSocket используется для realtime-обновлений.
- Через WebSocket можно:
  - отправлять текстовые сообщения;
  - отправлять сообщения с уже загруженными вложениями;
  - получать новые сообщения;
  - получать обновления статусов (`status`, `read_through`);
  - получать события редактирования;
  - получать события удаления;
  - отправлять и получать typing-события;
  - отмечать прочтение (`read`, `read_through`).
- Сообщения с файлами «в одном запросе» — через REST `POST /chats/{deal_id}/messages` (`multipart/form-data`).
- Сообщения с предзагрузкой — `POST /chats/{deal_id}/attachments`, затем JSON REST или WS `message` с `attachment_ids`.
- События `new_message`, `message_updated`, `message_deleted` рассылаются и при соответствующих REST-запросах, не только при действиях через WS.
