from fastapi import APIRouter

from . import auth, surveys, responses, analytics


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])
api_router.include_router(responses.router, tags=["responses"])
api_router.include_router(analytics.router, prefix="/surveys", tags=["analytics"])


