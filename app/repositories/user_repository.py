from typing import Generic, TypeVar

from app.db.base import Base
from app.models import User

if TYPE_CHECKING:
    from uuid import UUID


ModelType = TypeVar("ModelType", bound=Base)
UserType = TypeVar("UserType", bound=User)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository."""

    def __init__(self, query_model: type[ModelType]) -> None:
        self._query_model = query_model

    async def get(self, db, id) -> ModelType | None:
        return await db.get(self._query_model, id)

    async def get_all(self, db) -> list[ModelType]:
        result = await db.execute(select(self._query_model))
        return result.scalars().all()

    async def create(self, db, obj_in) -> ModelType:
        obj = self._query_model(**obj_in.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db, id, obj_in) -> ModelType:
        obj = await db.get(self._query_model, id)
        if not obj:
            raise ValueError("Object not found")
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def delete(self, db, id) -> bool:
        obj = await db.get(self._query_model, id)
        if not obj:
            return False
        await db.delete(obj)
        await db.commit()
        return True


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    # Add custom query methods if needed
    async def get_by_email(self, db, email: str) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_username(self, db, username: str) -> User | None:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()