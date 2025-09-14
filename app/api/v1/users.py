from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

import app.services.user as service
from app.core.auth import authorize_admin, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import PasswordChange, Token, UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    return service.create_user(user_in, session)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    return service.login_user(form_data.username, form_data.password, session)


@router.get("/", response_model=list[UserOut])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
    user: User = Depends(authorize_admin("users:read")),
):
    return service.get_users(skip, limit, session=session)


@router.get("/{resource_id}", response_model=UserOut)
async def get_user_by_id(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(authorize_admin("users:read")),
):
    return service.get_user_by_id(resource_id, session)


@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return service.change_password(session, user, password_change)


@router.delete("/{resource_id}", response_model=UserOut)
async def delete_user_by_id(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(authorize_admin("users:delete")),
):
    return service.delete_user_by_id(resource_id, session)
