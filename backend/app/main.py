import subprocess
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def get_application() -> FastAPI:
    app = FastAPI(
        title="Online Surveys API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.api.v1.api import api_router

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd="/app",
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print(f"Warning: Migration failed: {result.stderr}", file=sys.stderr)
            else:
                print("✓ Database migrations applied successfully")
        except Exception as e:
            print(f"Warning: Could not run migrations: {e}", file=sys.stderr)

    return app


app = get_application()


