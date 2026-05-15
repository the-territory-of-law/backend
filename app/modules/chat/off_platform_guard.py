"""
Увод общения в сторонние мессенджеры:

1) Ollama (локальная нейросеть) — основная проверка, если включено в настройках.
2) Эвристики — запас, если модель пропустила, или если Ollama недоступен.

Без Ollama: выставьте OFF_PLATFORM_OLLAMA_ENABLED=false или пустой OLLAMA_BASE_URL.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.core.config import Settings
from app.core.ollama import moderate_text

logger = logging.getLogger(__name__)

_URL_RE = re.compile(
    r"(?i)\b("
    r"t\.me/|telegram\.me/|telegram\.dog/|wa\.me/|whatsapp\.com/|"
    r"discord\.gg/|discord\.com/invite/|viber://|signal\.me/|"
    r"ig\.me/|instagram\.com/|m\.me/|fb\.com/messages"
    r")\S*"
)

# Латиница и частые русские написания / обходы
_MESSENGER_TOKEN_RE = re.compile(
    r"(?i)(?<![\w])("
    r"telegram|телеграм|телеграма?|telega|телега|"
    r"whatsapp|whats\s*app|ватсап|вацап|вотсап|вотсапп|"
    r"viber|вайбер|"
    r"макс\s*месс|"
    r"discord|дискорд|"
    r"\bsignal\b|сигнал\s*месс|"
    r"skype|скайп|"
    r"zoom\.us|"
    r"vk\.com/im|vk\.me/"
    r")(?![\w])"
)

# «Напиши в …» без явного имени — слабый сигнал, только вместе с контактом выше не нужен
_PHONE_RE = re.compile(
    r"(?:\+?\d[\d\s\-()]{8,}\d)"
)


@dataclass(frozen=True)
class OffPlatformResult:
    blocked: bool
    reason: str | None


def check_off_platform_rules(text: str) -> OffPlatformResult:
    """Синхронная проверка без внешних сервисов."""
    t = text.strip()
    if not t:
        return OffPlatformResult(False, None)

    if _URL_RE.search(t):
        return OffPlatformResult(True, "Ссылка на внешний мессенджер или чат.")

    if _MESSENGER_TOKEN_RE.search(t):
        return OffPlatformResult(True, "Упоминание стороннего мессенджера или канала связи.")

    # Очень короткие «тг / тгк» и т.п.
    if re.search(r"(?i)\bтгк?\b", t) or re.search(r"(?i)\bтелег\b", t):
        return OffPlatformResult(True, "Упоминание Telegram (сокращение).")

    if _PHONE_RE.search(t) and re.search(
        r"(?i)(позвон|набер|смс|whatsapp|ватсап|телег|telegram|viber|вайбер|связ)",
        t,
    ):
        return OffPlatformResult(True, "Телефон в контексте связи вне платформы.")

    return OffPlatformResult(False, None)


async def check_off_platform(text: str, settings: Settings | None = None) -> OffPlatformResult:
    """Сначала Ollama (если включено), затем эвристики — догоняют пропуски и срабатывают без LLM."""
    cfg = settings or Settings()
    if cfg.OFF_PLATFORM_OLLAMA_ENABLED and cfg.OLLAMA_BASE_URL:
        neural = await moderate_text(text, cfg)
        if neural.blocked:
            return OffPlatformResult(True, neural.reason)
        if neural.ollama_error:
            logger.warning("Ollama unavailable, using heuristics: %s", neural.ollama_error)
    return check_off_platform_rules(text)
