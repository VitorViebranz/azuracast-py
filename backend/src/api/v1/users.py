import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.dependencies import get_current_user, require_permission
from src.modules.users.models import User
from src.modules.users.schemas import UserResponse, UserUpdate
from src.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse], summary="List users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("admin:users")),
):
    service = UserService(db)
    return await service.list_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, summary="Get user")
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if (
        not current_user.is_super_admin
        and current_user.id != user_id
        and not current_user.has_permission("admin:users")
    ):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    service = UserService(db)
    return await service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("admin:users")),
):
    service = UserService(db)
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=204, summary="Delete user")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("admin:users")),
):
    service = UserService(db)
    await service.delete_user(user_id)
