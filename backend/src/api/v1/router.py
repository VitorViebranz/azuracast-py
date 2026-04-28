from fastapi import APIRouter

from src.api.v1 import auth, health, mount_points, stations, users

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(stations.router)
api_v1_router.include_router(mount_points.router)
