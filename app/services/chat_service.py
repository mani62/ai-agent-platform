from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.chat import Chat
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatCreate, ChatUpdate


class ChatService:

    def __init__(self):
        self.chat_repository = ChatRepository()
        self.agent_repository = AgentRepository()

    def create(
        self,
        db: Session,
        data: ChatCreate,
        current_user: User,
    ) -> Chat:

        agent = self.agent_repository.get_by_uuid_and_user(
            db,
            data.agent_uuid,
            current_user.id,
        )

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        if not agent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent is inactive",
            )

        chat = Chat(
            user_id=current_user.id,
            agent_id=agent.id,
            title=None,
        )

        return self.chat_repository.create(
            db,
            chat,
        )
    
    def get_my_chats(
        self,
        db: Session,
        current_user: User,
    ) -> list[Chat]:
        return self.chat_repository.get_all_by_user(
            db,
            current_user.id,
        )
    
    def get_chat(
        self,
        db: Session,
        current_user: User,
        uuid: str,
    ) -> Chat:

        chat = self.chat_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return chat
    
    def update_chat(
        self,
        db: Session,
        current_user: User,
        uuid: str,
        data: ChatUpdate,
    ) -> Chat:

        chat = self.chat_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(chat, field, value)

        return self.chat_repository.save(
            db,
            chat,
        )
    
    def delete_chat(
        self,
        db: Session,
        current_user: User,
        uuid: str,
    ) -> None:

        chat = self.chat_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        self.chat_repository.soft_delete(
            db,
            chat,
        )

        