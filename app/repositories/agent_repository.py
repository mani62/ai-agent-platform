from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.repositories.base_repository import BaseRepository

class AgentRepository(BaseRepository[Agent]):
    def __init__(self):
        super().__init__(Agent)

    def get_all_by_user(
        self,
        db: Session,
        user_id: int
    ) -> list[Agent]:
        return db.query(Agent).filter(
            Agent.user_id == user_id,
            Agent.deleted_at.is_(None)
        ).all()
    
    def get_by_uuid_and_user(
        self,
        db: Session,
        uuid: str,
        user_id: int,
    ) -> Agent | None:
        return (
            db.query(Agent)
            .filter(
                Agent.uuid == uuid,
                Agent.user_id == user_id,
                Agent.deleted_at.is_(None),
            )
            .first()
        )


