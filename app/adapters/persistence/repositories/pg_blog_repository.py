import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.mappers.blog_mapper import BlogMapper
from app.adapters.persistence.models.blog_model import BlogModel
from app.application.ports.repositories.blog_repository import BlogRepository
from app.domain.entities.blog import Blog
from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class PgBlogRepository(BlogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, blog: Blog) -> Blog:
        model = BlogMapper.to_model(blog)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return BlogMapper.to_entity(model)

    async def get_by_id(self, blog_id: uuid.UUID) -> Blog | None:
        result = await self._session.execute(select(BlogModel).where(BlogModel.id == blog_id))
        model = result.scalar_one_or_none()
        return BlogMapper.to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Blog]:
        result = await self._session.execute(select(BlogModel).where(BlogModel.user_id == user_id))
        return [BlogMapper.to_entity(m) for m in result.scalars().all()]

    async def update(self, blog: Blog) -> Blog:
        result = await self._session.execute(select(BlogModel).where(BlogModel.id == blog.id))
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Blog", str(blog.id))
        updated = BlogMapper.to_model(blog)

        for key in ("title", "url", "platform", "date", "description"):
            setattr(model, key, getattr(updated, key))

        await self._session.flush()
        await self._session.refresh(model)
        return BlogMapper.to_entity(model)

    async def delete(self, blog_id: uuid.UUID) -> None:
        result = await self._session.execute(select(BlogModel).where(BlogModel.id == blog_id))
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def bulk_create(self, blogs: list[Blog]) -> list[Blog]:
        models = [BlogMapper.to_model(b) for b in blogs]
        self._session.add_all(models)
        await self._session.flush()
        return [BlogMapper.to_entity(m) for m in models]

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self._session.execute(delete(BlogModel).where(BlogModel.user_id == user_id))
        await self._session.flush()
