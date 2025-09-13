from app.models.user import User


def has_permission(user: User, permission_name: str) -> bool:
    for role in user.roles:
        if any(p.name == permission_name for p in role.permissions):
            return True
    return False
