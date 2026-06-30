import asyncio
import sys
from enum import Enum
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.infrastructure.services.email.service import SMTPEmailService

# Set Windows event loop policy BEFORE anything else (before uvicorn/FastAPI creates the loop)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

from app.bootstrap import create_app
from app.core.config import get_settings
from app.infrastructure.services.email.resend_service import ResendEmailService

app = create_app()
settings = get_settings()




if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        reload_dirs=["app"],
    )
