from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.db.models import User
from app.db.schemas import UserCreate
from app.db.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvalidCredentialsError,
)


class UserService:
    """
    Service layer for User operations.

    All business logic related to users should go here:
    - Creating/updating/deleting users
    - Authentication
    - Permission checks (if needed)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserCreate) -> User:
        """Create a new user."""
        # Check if username or email already exists
        existing_user = await self.db.execute(
            """
            SELECT id FROM users
            WHERE username = :username OR email = :email
            """,
            {"username": user_in.username, "email": user_in.email},
        )
        if existing_user.fetchone():
            # Determine which field conflicts
            conflict = existing_user.keys()
            if "username" in conflict:
                raise EntityAlreadyExistsError("User", "username", user_in.username)
            else:
                raise EntityAlreadyExistsError("User", "email", user_in.email)

        # Hash the password
        hashed_password = get_password_hash(user_in.password)

        # Create new user instance
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.get(User, user_id)
        return result

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}
        )
        return result.scalars().first()

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[User]:
        """Authenticate a user with username and password."""
        result = await self.db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}
        )
        user = result.scalars().first()
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        return user

    async def update_user(
        self, user_id: str, user_in: UserCreate
    ) -> Optional[User]:
        """Update a user's information."""
        # Check if user exists
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise EntityNotFoundError("User", user_id)

        # Check if another user already has the same username or email
        query = """
        SELECT id FROM users
        WHERE (username = :username OR email = :email)
        AND id != :user_id
        """
        result = await self.db.execute(
            query,
            {
                "username": user_in.username,
                "email": user_in.email,
                "user_id": user_id,
            },
        )
        if result.fetchone():
            conflict = result.keys()
            if "username" in conflict:
                raise EntityAlreadyExistsError("User", "username", user_in.username)
            else:
                raise EntityAlreadyExistsError("User", "email", user_in.email)

        # Update fields
        for field in ["username", "email", "full_name", "password"]:
            if field in user_in.model_set(by_alias=True):
                setattr(existing_user, field, getattr(user_in, field))

        # Hash password if changed
        if hasattr(user_in, "password") and user_in.password is not None:
            existing_user.hashed_password = get_password_hash(user_in.password)

        await self.db.commit()
        await self.db.refresh(existing_user)
        return existing_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def get_users_paginated(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get a paginated list of users."""
        result = await self.db.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
            {"limit": limit, "skip": skip},
        )
        return result.scalars().all()