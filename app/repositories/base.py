from typing import Generic, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.query import Query

from app.db.base import Base
from app.models import BaseModel


if TYPE_CHECKING:
    from uuid import UUID


class BaseRepository(Generic[Base]):
    """Generic CRUD repository."""

    def __init__(self, query_model: type[Base]):
        self._query_model = query_model

    async def get(self, db, id) -> Optional[Base]:
        result = await db.get(self._query_model, id)
        return result

    async def get_all(self, db) -> List[Base]:
        result = await db.execute(select(self._query_model))
        return result.scalars().all()

    async def create(self, db, obj_in) -> Base:
        obj = self._query_model(**obj_in.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db, obj_in) -> Base:
        obj = await db.get(self._query_model, obj_in.id)
        if not obj:
            raise ValueError("Object not found")
        for field, value in obj_in.model_dump().items():
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


class BaseService:
    """Base service layer class."""

    def __init__(self, repository):
        self.repository = repository


class BaseSchema:
    """Base Pydantic schema."""

    model_config = {"extra": "allow"}


class PydanticBaseModel:
    """Base Pydantic model."""

    def model_dump(self, **kwargs):
        return super().model_dump(**kwargs)