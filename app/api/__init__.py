# app/api/__init__.py
from fastapi import APIRouter
from app.core.config import settings

# Import versioned routers dynamically
if settings.API_VERSION == "v1":
    from app.api.v1 import notes, users
# elif API_VERSION == "v2":
#     from app.api.v2 import notes, users

router = APIRouter(prefix=settings.API_PREFIX, tags=[settings.API_VERSION])

router.include_router(users.router)
router.include_router(notes.router)

@router.get("/health")
def health_check():
    return {"status": "ok"}
