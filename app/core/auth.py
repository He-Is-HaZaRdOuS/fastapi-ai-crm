from typing import Callable
import inspect
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session
from typing import List, Optional

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.services.rbac import has_permission
from app.services.user import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/users/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email, session)
    if user is None:
        raise credentials_exception
    return user

def authorize_user_or_admin(
    permission_name: str,
    get_resource_owner: Callable[[int], int],  # function to get owner_id from resource_id
):
    async def dependency(
        resource_id: Optional[int] = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
    ):
        # Check role/permission
        if any(role.has_permission(permission_name) for role in current_user.roles):
            return current_user

        if get_resource_owner is None:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Check ownership
        owner_id = get_resource_owner(resource_id, session) if resource_id else None
        if owner_id is None:
            if has_permission(current_user, permission_name):
                raise HTTPException(status_code=404, detail="Resource not found")
            else:
                raise HTTPException(status_code=403, detail="Forbidden")

        if current_user.id == owner_id:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource"
        )

    return dependency

def authorize_admin(
    permission_name: str,
):
    async def dependency(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
    ):
        # Check role/permission
        if any(role.has_permission(permission_name) for role in current_user.roles):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource"
        )

    return dependency
