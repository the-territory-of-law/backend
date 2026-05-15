from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import Settings
from app.core.ollama import check_ollama_health
from app.core.startup_ollama import prepare_ollama_on_startup
from app.modules.auth.router import router as auth_router
from app.modules.chat.router import router as chat_router
from app.modules.chat.ws_routes import router as chat_ws_router
from app.modules.users.router import router as users_router

settings = Settings()
Path(settings.CHAT_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await prepare_ollama_on_startup(settings)
    yield


app = FastAPI(title="Backend service", lifespan=lifespan)

_cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(chat_ws_router)
app.mount(
    settings.CHAT_STATIC_MOUNT,
    StaticFiles(directory=settings.CHAT_UPLOAD_DIR),
    name="chat_uploads",
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ollama", tags=["health"])
async def health_ollama() -> dict:
    h = await check_ollama_health(settings)
    return {
        "enabled": h.enabled,
        "base_url": h.base_url,
        "model": h.model,
        "reachable": h.reachable,
        "model_available": h.model_available,
        "installed_models": list(h.installed_models),
        "error": h.error,
        "ready": h.enabled and h.reachable and h.model_available,
    }
