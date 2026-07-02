"""
Dependency Injection Container.
Wires concrete implementations to abstract ports.
All use cases receive dependencies through here — never import concrete classes directly.
"""

from functools import lru_cache

from lagom import Container


@lru_cache(maxsize=1)
def get_container() -> Container:
    container = Container()

    # ── Infrastructure ────────────────────────────────────────────────────────
    # Registered lazily — filled in as phases are implemented

    # ── Repositories ──────────────────────────────────────────────────────────
    # from app.adapters.persistence.repositories.pg_user_repository import PgUserRepository
    # from app.application.ports.repositories.user_repository import UserRepository
    # container.define(UserRepository, lambda: PgUserRepository(...))

    # ── AI Ports ──────────────────────────────────────────────────────────────
    # from app.adapters.ai.agents.resume_parser_agent import ResumeParserAgent
    # from app.application.ports.ai.resume_parser_port import ResumeParserPort
    # container.define(ResumeParserPort, lambda: ResumeParserAgent())

    # ── Storage ───────────────────────────────────────────────────────────────
    # from app.adapters.storage.r2_file_storage import R2FileStorage
    # from app.application.ports.storage.file_storage_port import FileStoragePort
    # container.define(FileStoragePort, lambda: R2FileStorage())

    return container
