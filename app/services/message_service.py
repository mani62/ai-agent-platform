from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.enums import MessageRole
from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message import MessageCreate

from app.services.llm_service import LLMService
from app.ai.agents.runner import AgentRunner

class MessageService:

    def __init__(self):
        self.message_repository = MessageRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()
        self.agent_runner = AgentRunner()

    def create(
        self,
        db: Session,
        chat_uuid: str,
        data: MessageCreate,
        current_user: User,
    ) -> Message:

        chat = self._get_chat(
            db,
            chat_uuid,
            current_user,
        )

        self._create_user_message(
            db,
            chat.id,
            data.content,
        )

        history = self.message_repository.get_all_by_chat(
            db,
            chat.id,
        )

        assistant_content = self.agent_runner.run(
            agent=chat.agent,
            history=history,
        )

        assistant_message = self._create_assistant_message(
            db,
            chat.id,
            assistant_content,
        )

        self._generate_chat_title_if_needed(
            db,
            chat,
            data.content,
        )

        return assistant_message
    
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
    
    def _get_chat(
        self,
        db: Session,
        chat_uuid: str,
        current_user: User,
    ) -> Chat:

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

        return chat

    def _create_user_message(
        self,
        db: Session,
        chat_id: int,
        content: str,
    ) -> Message:

        message = Message(
            chat_id=chat_id,
            role=MessageRole.USER,
            content=content,
        )

        return self.message_repository.create(
            db,
            message,
        )

    def _create_assistant_message(
        self,
        db: Session,
        chat_id: int,
        content: str,
    ) -> Message:

        message = Message(
            chat_id=chat_id,
            role=MessageRole.ASSISTANT,
            content=content,
        )

        return self.message_repository.create(
            db,
            message,
        )

    def _generate_chat_title_if_needed(
        self,
        db: Session,
        chat: Chat,
        first_message: str,
    ) -> None:

        if chat.title is not None:
            return

        title = self.llm_service.generate_chat_title(
            provider=chat.agent.provider,
            model=chat.agent.model,
            first_message=first_message,
        )

        chat.title = title

        self.chat_repository.save(
            db,
            chat,
        )