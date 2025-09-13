from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

import app.services.user as service
from app.core.auth import authorize_admin
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import PasswordChange, Token, UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    user = service.create_user(user_in, session)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = service.authenticate_user(
        form_data.username, form_data.password, session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/", response_model=list[UserOut])
async def get_users(
    session: Session = Depends(get_session),
    user: User = authorize_admin("users:read"),
):
    return service.get_users(session)


@router.get("/{resource_id}", response_model=UserOut)
async def get_user_by_id(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = authorize_admin("users:read"),
):
    return service.get_user_by_id(resource_id, session)


@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    session: Session = Depends(get_session),
    user: User = authorize_admin("users:update"),
):
    return service.change_password(session, user, password_change)


@router.delete("/{resource_id}", response_model=UserOut)
async def delete_user_by_id(
    resource_id: int,
    session: Session = Depends(get_session),
    user: User = authorize_admin("users:delete"),
):
    return service.delete_user_by_id(resource_id, session)
