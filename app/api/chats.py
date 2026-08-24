from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.chat import Chat
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

chat_service = ChatService()

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.create(
        db,
        data,
        current_user,
    )

@router.get(
    "",
    response_model=list[ChatResponse],
)
def get_my_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_my_chats(
        db,
        current_user,
    )

@router.get(
    "/{uuid}",
    response_model=ChatResponse,
)
def get_chat(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_chat(
        db,
        current_user,
        uuid,
    )

@router.patch(
    "/{uuid}",
    response_model=ChatResponse,
)
def update_chat(
    uuid: str,
    data: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.update_chat(
        db,
        current_user,
        uuid,
        data,
    )

@router.delete(
    "/{uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chat(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:

    chat_service.delete_chat(
        db,
        current_user,
        uuid,
    )
