"""Клиент Ollama: health-check, загрузка модели, модерация текста чата."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.core.config import Settings

logger = logging.getLogger(__name__)

_MODERATION_SYSTEM = (
    "Ты модератор платформы «юрист — клиент». Ответь строго JSON с полями "
    '"blocked" (boolean) и "reason" (string или null). '
    "blocked=true, если пользователь предлагает связаться вне этого чата: "
    "Telegram/WhatsApp/Viber/Max/Signal/Discord, личные сообщения в соцсетях, "
    "никнейм для мессенджера, телефон/e-mail чтобы выйти на прямую связь, "
    "намёки («напиши в зелёном», «там же обсудим») при явном уводе. "
    "blocked=false для обычных юридических вопросов, ссылок на суды/законы/госуслуги "
    "без личного контакта."
)


@dataclass(frozen=True)
class OllamaHealth:
    enabled: bool
    base_url: str | None
    model: str
    reachable: bool
    model_available: bool
    installed_models: tuple[str, ...]
    error: str | None


@dataclass(frozen=True)
class OllamaModerationResult:
    blocked: bool
    reason: str | None
    used_ollama: bool
    ollama_error: str | None = None


def _request_json(
    method: str,
    url: str,
    payload: dict | None = None,
    timeout_sec: float = 10.0,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_ollama_health_sync(settings: Settings | None = None) -> OllamaHealth:
    cfg = settings or Settings()
    base = cfg.OLLAMA_BASE_URL
    model = cfg.OLLAMA_MODEL
    if not cfg.OFF_PLATFORM_OLLAMA_ENABLED or not base:
        return OllamaHealth(
            enabled=False,
            base_url=base,
            model=model,
            reachable=False,
            model_available=False,
            installed_models=(),
            error=None,
        )

    tags_url = f"{base.rstrip('/')}/api/tags"
    try:
        body = _request_json("GET", tags_url, timeout_sec=min(cfg.OLLAMA_REQUEST_TIMEOUT_SEC, 10.0))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return OllamaHealth(
            enabled=True,
            base_url=base,
            model=model,
            reachable=False,
            model_available=False,
            installed_models=(),
            error=str(exc),
        )

    names: list[str] = []
    for item in body.get("models") or []:
        name = item.get("name")
        if isinstance(name, str) and name:
            names.append(name)

    model_available = any(
        n == model or n.startswith(f"{model}:") or n.split(":")[0] == model
        for n in names
    )
    return OllamaHealth(
        enabled=True,
        base_url=base,
        model=model,
        reachable=True,
        model_available=model_available,
        installed_models=tuple(names),
        error=None if model_available else f"Model '{model}' not found. Run: ollama pull {model}",
    )


def pull_model_sync(settings: Settings | None = None) -> None:
    cfg = settings or Settings()
    if not cfg.OLLAMA_BASE_URL:
        raise RuntimeError("OLLAMA_BASE_URL is not set")
    url = f"{cfg.OLLAMA_BASE_URL.rstrip('/')}/api/pull"
    _request_json(
        "POST",
        url,
        {"name": cfg.OLLAMA_MODEL, "stream": False},
        timeout_sec=max(cfg.OLLAMA_REQUEST_TIMEOUT_SEC, 120.0),
    )


def moderate_text_sync(text: str, settings: Settings | None = None) -> OllamaModerationResult:
    cfg = settings or Settings()
    if not cfg.OFF_PLATFORM_OLLAMA_ENABLED or not cfg.OLLAMA_BASE_URL:
        return OllamaModerationResult(False, None, used_ollama=False)

    url = f"{cfg.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": cfg.OLLAMA_MODEL,
        "format": "json",
        "messages": [
            {"role": "system", "content": _MODERATION_SYSTEM},
            {"role": "user", "content": text[:4000]},
        ],
        "stream": False,
        "options": {"temperature": 0},
    }
    try:
        body = _request_json(
            "POST",
            url,
            payload,
            timeout_sec=cfg.OLLAMA_REQUEST_TIMEOUT_SEC,
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.warning("Ollama moderation request failed: %s", exc)
        return OllamaModerationResult(False, None, used_ollama=True, ollama_error=str(exc))

    raw = (body.get("message") or {}).get("content") or ""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Ollama returned non-JSON: %s", raw[:200])
        return OllamaModerationResult(
            False, None, used_ollama=True, ollama_error="invalid_json_response"
        )

    blocked = bool(data.get("blocked"))
    reason = data.get("reason")
    if blocked and not isinstance(reason, str):
        reason = "Политика платформы: общение только в этом чате."
    return OllamaModerationResult(blocked, reason if blocked else None, used_ollama=True)


async def check_ollama_health(settings: Settings | None = None) -> OllamaHealth:
    return await asyncio.to_thread(check_ollama_health_sync, settings)


async def pull_model(settings: Settings | None = None) -> None:
    await asyncio.to_thread(pull_model_sync, settings)


async def moderate_text(text: str, settings: Settings | None = None) -> OllamaModerationResult:
    return await asyncio.to_thread(moderate_text_sync, text, settings)
