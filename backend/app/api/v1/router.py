from fastapi import APIRouter
from app.api.v1.leagues import router as leagues_router
from app.api.v1.clubs import router as clubs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.standings import router as standings_router
from app.api.v1.sync import router as sync_router

# Asosiy v1 router - barcha sub-routerlarni birlashtiradi
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(leagues_router)
api_v1_router.include_router(clubs_router)
api_v1_router.include_router(matches_router)
api_v1_router.include_router(standings_router)
api_v1_router.include_router(sync_router)
