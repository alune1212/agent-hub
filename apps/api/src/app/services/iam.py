from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Role, RolePermission, User, UserRole


@dataclass(slots=True)
class UserProfileData:
    user_id: str
    user_name: str
    email: str | None
    roles: list[str]
    permissions: list[str]


async def upsert_user(
    session: AsyncSession,
    user_id: str,
    user_name: str,
    email: str | None = None,
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        user = User(user_id=user_id, user_name=user_name, email=email, is_active=True)
        session.add(user)
    else:
        user.user_name = user_name
        user.email = email
    await session.flush()
    return user


async def set_user_roles(session: AsyncSession, user_id: str, roles: list[str]) -> None:
    await session.execute(delete(UserRole).where(UserRole.user_id == user_id))

    if not roles:
        return

    existing_roles = await session.execute(select(Role.role_id).where(Role.role_id.in_(roles)))
    valid_roles = {row[0] for row in existing_roles.all()}

    for role_id in sorted(valid_roles):
        session.add(UserRole(user_id=user_id, role_id=role_id))

    await session.flush()


async def ensure_default_role(session: AsyncSession, user_id: str, default_role: str = "employee") -> None:
    role_rows = await session.execute(select(UserRole.role_id).where(UserRole.user_id == user_id))
    if role_rows.first() is not None:
        return

    role_exists = await session.get(Role, default_role)
    if role_exists is None:
        return

    session.add(UserRole(user_id=user_id, role_id=default_role))
    await session.flush()


async def get_user_profile(session: AsyncSession, user_id: str) -> UserProfileData:
    user = await session.get(User, user_id)
    if user is None:
        raise ValueError(f"user not found: {user_id}")

    role_rows = await session.execute(select(UserRole.role_id).where(UserRole.user_id == user_id))
    roles = sorted({row[0] for row in role_rows.all()})

    permission_rows = await session.execute(
        select(RolePermission.permission_key)
        .join(UserRole, RolePermission.role_id == UserRole.role_id)
        .where(UserRole.user_id == user_id)
    )
    permissions = sorted({row[0] for row in permission_rows.all()})

    return UserProfileData(
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        roles=roles,
        permissions=permissions,
    )
