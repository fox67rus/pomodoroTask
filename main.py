import asyncio
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.db import engine
from app.models import Base
from app.routers import auth, dashboard, pomodoro, tasks

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from sqlalchemy.exc import OperationalError

    attempts = 30
    delay_sec = 1.0
    for attempt in range(1, attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError as exc:
            if attempt == attempts:
                logger.exception("Database unavailable after %s attempts", attempts)
                raise
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                attempts,
                exc,
            )
            await asyncio.sleep(delay_sec)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    templates = Jinja2Templates(directory="app/templates")
    app.state.templates = templates

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(dashboard.router)
    app.include_router(auth.router)
    app.include_router(tasks.router)
    app.include_router(pomodoro.router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        if request.url.path.startswith("/api"):
            from fastapi.exception_handlers import request_validation_exception_handler

            return await request_validation_exception_handler(request, exc)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return app


app = create_app()
