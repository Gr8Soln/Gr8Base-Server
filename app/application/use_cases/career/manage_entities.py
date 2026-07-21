import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from app.domain.exceptions.domain_exceptions import EntityNotFoundError


class EntityRepo(Protocol):
    async def get_by_id(self, entity_id: uuid.UUID) -> Any: ...
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Any]: ...
    async def create(self, entity: Any) -> Any: ...
    async def update(self, entity: Any) -> Any: ...
    async def delete(self, entity_id: uuid.UUID) -> None: ...


@dataclass
class CreateEntityInput:
    user_id: uuid.UUID
    data: dict


@dataclass
class UpdateEntityInput:
    entity_id: uuid.UUID
    user_id: uuid.UUID
    data: dict


@dataclass
class DeleteEntityInput:
    entity_id: uuid.UUID
    user_id: uuid.UUID


# ── Generic Use Cases ─────────────────────────────────────────────────────────

class CreateEntityUseCase:
    """Create a career profile entity (experience, project, skill, etc.)."""

    def __init__(self, repo: EntityRepo, entity_factory) -> None:
        self._repo = repo
        self._factory = entity_factory

    async def execute(self, data: CreateEntityInput) -> Any:
        entity = self._factory(user_id=data.user_id, **data.data)
        return await self._repo.create(entity)


class UpdateEntityUseCase:
    """Update a career profile entity."""

    def __init__(self, repo: EntityRepo) -> None:
        self._repo = repo

    async def execute(self, data: UpdateEntityInput) -> Any:
        entity = await self._repo.get_by_id(data.entity_id)
        if not entity:
            raise EntityNotFoundError("Entity", str(data.entity_id))
        for key, value in data.data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        return await self._repo.update(entity)


class DeleteEntityUseCase:
    """Delete a career profile entity."""

    def __init__(self, repo: EntityRepo) -> None:
        self._repo = repo

    async def execute(self, data: DeleteEntityInput) -> None:
        entity = await self._repo.get_by_id(data.entity_id)
        if not entity:
            raise EntityNotFoundError("Entity", str(data.entity_id))
        await self._repo.delete(data.entity_id)


class ListEntitiesUseCase:
    """List all entities of a type for a user."""

    def __init__(self, repo: EntityRepo) -> None:
        self._repo = repo

    async def execute(self, user_id: uuid.UUID) -> list[Any]:
        return await self._repo.get_by_user_id(user_id)
