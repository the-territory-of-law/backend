"""Проверка и подготовка Ollama при старте приложения."""

from __future__ import annotations

import logging

from app.core.config import Settings
from app.core.ollama import check_ollama_health, pull_model

logger = logging.getLogger(__name__)


async def prepare_ollama_on_startup(cfg: Settings) -> None:
    if not cfg.OFF_PLATFORM_OLLAMA_ENABLED or not cfg.OLLAMA_BASE_URL:
        logger.info("Ollama moderation disabled (OFF_PLATFORM_OLLAMA_ENABLED or OLLAMA_BASE_URL)")
        return

    health = await check_ollama_health(cfg)
    if not health.reachable:
        logger.warning(
            "Ollama not reachable at %s — chat moderation will use heuristics only. %s",
            cfg.OLLAMA_BASE_URL,
            health.error or "",
        )
        return

    if health.model_available:
        logger.info("Ollama ready: %s model=%s", cfg.OLLAMA_BASE_URL, cfg.OLLAMA_MODEL)
        return

    if not cfg.OLLAMA_PULL_ON_STARTUP:
        logger.warning(
            "Ollama model '%s' not installed. Run: ollama pull %s",
            cfg.OLLAMA_MODEL,
            cfg.OLLAMA_MODEL,
        )
        return

    logger.info("Pulling Ollama model %s on startup...", cfg.OLLAMA_MODEL)
    try:
        await pull_model(cfg)
        health = await check_ollama_health(cfg)
        if health.model_available:
            logger.info("Ollama model %s ready", cfg.OLLAMA_MODEL)
        else:
            logger.warning("Model pull finished but %s still not listed", cfg.OLLAMA_MODEL)
    except Exception as exc:
        logger.warning("Ollama pull on startup failed: %s", exc)
