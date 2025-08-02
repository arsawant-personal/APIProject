from fastapi import APIRouter
from app.api.v1 import admin, auth, external

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(external.router) 