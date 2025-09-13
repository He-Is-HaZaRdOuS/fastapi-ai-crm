from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User, UserRoleLink

class RolePermissionLink(SQLModel, table=True):
    role_id: Optional[int] = Field(foreign_key="role.id", primary_key=True)
    permission_id: Optional[int] = Field(
        foreign_key="permission.id", primary_key=True
    )

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermissionLink
    )
    users: List[User] = Relationship(
        back_populates="roles", link_model=UserRoleLink
    )

    def has_permission(self, permission_name: str) -> bool:
        return any(p.name == permission_name for p in self.permissions)


class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    roles: List[Role] = Relationship(
        back_populates="permissions", link_model=RolePermissionLink
    )
