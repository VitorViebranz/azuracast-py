"""Seed script to populate initial data."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.modules.users.models import Permission, Role, User
from sqlalchemy import select


ROLES = [
    {"name": "superadmin", "description": "Full system access"},
    {"name": "admin", "description": "Administrative access"},
    {"name": "viewer", "description": "Read-only access"},
]

PERMISSIONS = [
    {"name": "station:view", "description": "View stations"},
    {"name": "station:edit", "description": "Edit stations"},
    {"name": "station:delete", "description": "Delete stations"},
    {"name": "admin:users", "description": "Manage users"},
    {"name": "admin:roles", "description": "Manage roles"},
    {"name": "admin:settings", "description": "Manage settings"},
]


async def seed():
    async with AsyncSessionLocal() as db:
        perms = {}
        for pdata in PERMISSIONS:
            result = await db.execute(select(Permission).where(Permission.name == pdata["name"]))
            perm = result.scalar_one_or_none()
            if not perm:
                perm = Permission(**pdata)
                db.add(perm)
                await db.flush()
            perms[pdata["name"]] = perm

        roles = {}
        for rdata in ROLES:
            result = await db.execute(select(Role).where(Role.name == rdata["name"]))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(**rdata)
                db.add(role)
                await db.flush()
            roles[rdata["name"]] = role

        for perm in perms.values():
            if perm not in roles["superadmin"].permissions:
                roles["superadmin"].permissions.append(perm)

        for pname in ["station:view", "station:edit", "admin:users"]:
            if perms[pname] not in roles["admin"].permissions:
                roles["admin"].permissions.append(perms[pname])

        if perms["station:view"] not in roles["viewer"].permissions:
            roles["viewer"].permissions.append(perms["station:view"])

        result = await db.execute(select(User).where(User.email == "admin@azuracast.local"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@azuracast.local",
                username="admin",
                display_name="Administrator",
                password_hash=hash_password("admin123"),
                is_active=True,
                is_super_admin=True,
            )
            admin.roles.append(roles["superadmin"])
            db.add(admin)

        await db.commit()
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
