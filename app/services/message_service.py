from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message import MessageCreate

from app.services.llm_service import LLMService

class MessageService:

    def __init__(self):
        self.message_repository = MessageRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()

    def create(
        self,
        db: Session,
        chat_uuid: str,
        data: MessageCreate,
        current_user: User,
    ) -> Message:

        chat = self.chat_repository.get_by_uuid_and_user(
            db,
            chat_uuid,
            current_user.id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        user_message = Message(
            chat_id=chat.id,
            role="user",
            content=data.content,
        )

        self.message_repository.create(
            db,
            user_message,
        )

        history = self.message_repository.get_all_by_chat(
            db,
            chat.id,
        )

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in history
        ]

        assistant_content = self.llm_service.generate_response(
            provider=chat.agent.provider,
            model=chat.agent.model,
            system_prompt=chat.agent.system_prompt,
            messages=messages,
        )

        assistant_message = Message(
            chat_id=chat.id,
            role="assistant",
            content=assistant_content,
        )

        return self.message_repository.create(
            db,
            assistant_message,
        )
    
    def get_messages(
        self,
        db: Session,
        chat_uuid: str,
        current_user: User,
    ) -> list[Message]:

        chat = self.chat_repository.get_by_uuid_and_user(
            db,
            chat_uuid,
            current_user.id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return self.message_repository.get_all_by_chat(
            db,
            chat.id,
        )