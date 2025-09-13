import tomli
from sqlmodel import Session, select
from app.models.user import User
from app.models.rbac import Role, Permission
from app.core.security import hash_password

def init_rbac(session: Session, toml_path: str = "configuration/rbac_config.toml"):
    with open(toml_path, "rb") as f:
        config = tomli.load(f)

    # Create roles and permissions
    for role_name, data in config.get("roles", {}).items():
        permissions = data.get("permissions", [])

        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if not role:
            role = Role(name=role_name)
            session.add(role)
            session.commit()
            session.refresh(role)

        # Create permissions and associate with role
        for perm_name in permissions:
            perm = session.exec(select(Permission).where(Permission.name == perm_name)).first()
            if not perm:
                perm = Permission(name=perm_name)
                session.add(perm)
                session.commit()
                session.refresh(perm)

            if perm not in role.permissions:
                role.permissions.append(perm)
                session.add(role)
        session.commit()

    # Create admin users
    for email in config.get("users", {}).get("admins", {}).get("emails", []):
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            hashed_pw = hash_password(email)  # password = email for initial setup
            user = User(email=email, hashed_password=hashed_pw)
            session.add(user)
            session.commit()
            session.refresh(user)

        # Assign ADMIN role
        admin_role = session.exec(select(Role).where(Role.name == "ADMIN")).first()
        if admin_role not in user.roles:
            user.roles.append(admin_role)
            session.add(user)
            session.commit()
