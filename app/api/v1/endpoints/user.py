from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_password_hash
from app.db.models import User
from app.db.schemas import UserCreate, UserOut, UserUpdate
from app.db.dependencies import get_db
from app.services.user import UserService

router = APIRouter()


@router.post("/", response_model=UserOut)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    service = UserService(db)
    user = await service.create_user(user_in)
    return user


@router.get("/", response_model=list[UserOut])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve list of users."""
    service = UserService(db)
    users = await service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a user by ID."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user."""
    service = UserService(db)
    user = await service.update_user(user_id, user_in)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user."""
    service = UserService(db)
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}