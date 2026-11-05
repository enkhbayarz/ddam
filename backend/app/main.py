import logging

from fastapi import FastAPI

from app.api import chat, conversations, health, personas
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.middleware import register_middleware

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    register_middleware(app, settings)
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    app.include_router(personas.router, prefix="/api")
    app.include_router(conversations.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    return app


app = create_app()
