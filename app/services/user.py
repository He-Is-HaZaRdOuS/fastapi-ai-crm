from datetime import timedelta

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.exceptions import (
    InvalidPasswordError,
    PasswordMismatchError,
    PaswordRequirementsNotMetError,
    UserError,
    UserNotFoundError,
    AuthenticationError,
    TokenError
)
from app.core.input_validator import email_is_valid, password_is_valid
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_session
from app.models.rbac import Role
from app.models.user import User, UserRoleLink
from app.schemas.user import PasswordChange, UserCreate


def get_users(skip: int, limit: int, session: Session = Depends(get_session)):
    return session.exec(select(User).offset(skip).limit(limit)).all()


def get_user_by_email(
    email: str, session: Session = Depends(get_session)
) -> User | None:
    result = session.exec(select(User).where(User.email == email))
    return result.first()


def get_user_by_id(
    user_id: int, session: Session = Depends(get_session)
) -> User | None:
    result = session.exec(select(User).where(User.id == user_id))
    return result.first()


def delete_user_by_id(
    user_id: int, session: Session = Depends(get_session)
) -> User | None:
    result = session.exec(select(User).where(User.id == user_id)).first()
    if result is None:
        raise UserNotFoundError
    session.delete(result)
    session.commit()
    return result


def create_user(
    user_in: UserCreate, session: Session = Depends(get_session)
) -> User:
    if not email_is_valid(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format",
        )
    if not password_is_valid(user_in.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character",
        )

    hashed_pw = hash_password(user_in.password)
    db_user = User(email=user_in.email, hashed_password=hashed_pw)
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)

        agent_role = session.exec(
            select(Role).where(Role.name == "AGENT")
        ).first()
        if agent_role:
            session.add(UserRoleLink(user_id=db_user.id, role_id=agent_role.id))
            session.commit()

        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )


def change_password(
    session: Session, user: User, password_change: PasswordChange
) -> None:
    try:
        if user is None:
            raise UserNotFoundError

        # Verify current password
        if not verify_password(
            password_change.current_password, user.hashed_password
        ):
            raise InvalidPasswordError()

        if not password_is_valid(password_change.new_password):
            raise PaswordRequirementsNotMetError

        # Verify new passwords match
        if password_change.new_password != password_change.new_password_confirm:
            raise PasswordMismatchError()

        # Update password
        user.hashed_password = hash_password(password_change.new_password)
        session.commit()
    except Exception as e:
        raise


def login_user(username: str, password: str, session: Session) -> dict:
    user = authenticate_user(username.lower(), password, session)

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    if not token:
        raise TokenError
    return {"access_token": token, "token_type": "bearer"}


def authenticate_user(
    email: str, password: str, session: Session = Depends(get_session)
) -> User | None:
    user = get_user_by_email(email, session)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthenticationError
    return user
