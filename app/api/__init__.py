from fastapi import APIRouter

from app.api import users

router = APIRouter()
router.include_router(users.router)


@router.get("/health")
def health_check():
    return {"status": "ok"}
