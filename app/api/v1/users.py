from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

import app.services.user as service
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserOut

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
async def list_users(session: Session = Depends(get_session)):
    return service.get_users(session)
