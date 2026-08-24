from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService


router = APIRouter(
    tags=["Messages"],
)

message_service = MessageService()


@router.post(
    "/chats/{chat_uuid}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    chat_uuid: str,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.create(
        db,
        chat_uuid,
        data,
        current_user,
    )

@router.get(
    "/chats/{chat_uuid}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    chat_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.get_messages(
        db,
        chat_uuid,
        current_user,
    )