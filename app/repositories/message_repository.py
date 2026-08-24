from pytest import Session
from app.models.message import Message
from app.repositories.base_repository import BaseRepository


class MessageRepository(BaseRepository[Message]):

    def __init__(self):
        super().__init__(Message)

    def get_all_by_chat(
        self,
        db: Session,
        chat_id: int,
    ) -> list[Message]:
        return (
            db.query(Message)
            .filter(
                Message.chat_id == chat_id,
                Message.deleted_at.is_(None),
            )
            .order_by(Message.created_at.asc())
            .all()
        )    