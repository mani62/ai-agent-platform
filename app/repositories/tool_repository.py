from sqlalchemy.orm import Session

from app.models.tool import Tool
from app.repositories.base_repository import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    def __init__(self):
        super().__init__(Tool)

    def get_by_name(
        self,
        db: Session,
        name: str,
    ) -> Tool | None:
        return (
            db.query(Tool)
            .filter(
                Tool.name == name,
                Tool.deleted_at.is_(None),
            )
            .first()
        )

    def get_by_uuids(
        self,
        db: Session,
        uuids: list[str],
    ) -> list[Tool]:
        return (
            db.query(Tool)
            .filter(
                Tool.uuid.in_(uuids),
                Tool.deleted_at.is_(None),
            )
            .all()
        )