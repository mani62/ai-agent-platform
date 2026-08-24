from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.repositories.base_repository import BaseRepository

class ChatRepository(BaseRepository[Chat]):
    def __init__(self):
        super().__init__(Chat)

    def create(
        self,
        db: Session,
        chat: Chat,
    ) -> Chat:
        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat
    
    def get_all_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[Chat]:
        return (
            db.query(Chat)
            .filter(
                Chat.user_id == user_id,
                Chat.deleted_at.is_(None),
            )
            .all()
        )
    
    def get_by_uuid_and_user(
        self,
        db: Session,
        uuid: str,
        user_id: int,
    ) -> Chat | None:
        return (
            db.query(Chat)
            .filter(
                Chat.uuid == uuid,
                Chat.user_id == user_id,
                Chat.deleted_at.is_(None),
            )
            .first()
        )