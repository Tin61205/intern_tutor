# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1 import users

api_router = APIRouter()

# Include các router con
api_router.include_router(users.router)
# api_router.include_router(workspaces.router) # Thêm sau
