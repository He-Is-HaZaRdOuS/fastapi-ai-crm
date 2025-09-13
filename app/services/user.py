from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.input_validator import email_is_valid, password_is_valid
from app.core.security import hash_password, verify_password
from app.core.exceptions import UserError, UserNotFoundError, PasswordMismatchError, InvalidPasswordError, PaswordRequirementsNotMetError
from app.db.session import get_session
from app.models.user import User, UserRoleLink
from app.models.rbac import Role
from app.schemas.user import UserCreate, PasswordChange


def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


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

        agent_role = session.exec(select(Role).where(Role.name == "AGENT")).first()
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

def change_password(session: Session, user: User, password_change: PasswordChange) -> None:
    try:
        if user is None:
            raise UserNotFoundError

        # Verify current password
        if not verify_password(password_change.current_password, user.hashed_password):
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


def authenticate_user(
    email: str, password: str, session: Session = Depends(get_session)
) -> User | None:
    user = get_user_by_email(email, session)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
