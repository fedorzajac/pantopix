"""main reservation logic"""

# import json
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import register_routers

logging.basicConfig(
    level=int(os.getenv("DEBUG_LEVEL")),  # integer in env.
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(ap: FastAPI):
    """Initialize database tables on application startup."""
    ap.state.cache = None
    ap.state.cache_expires = 0
    ap.state.cache_lock = asyncio.Lock()

    try:
        logging.info("Application starting")
        yield
    finally:
        logging.info("Application shutting down")


app = FastAPI(debug=True, title="FastAPI Quickstart", lifespan=lifespan)

STATIC_DIR = Path("app/static").resolve()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

register_routers(app=app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="__main__:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        reload_delay=3,
        log_level=os.getenv("DEBUG"),
    )
