from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.services.agent_service import AgentService

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)

agent_service = AgentService()

@router.post(
    "",
    response_model=AgentRead        
)
def create_agent(
    data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return agent_service.create(
        db=db,
        current_user=current_user,
        data=data,
    )

@router.get(
    "",
    response_model=list[AgentRead]
)
def get_my_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return agent_service.get_my_agents(
        db,
        current_user,
    )

@router.get(
    "/{uuid}",
    response_model=AgentRead,
)
def get_agents(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return agent_service.get_agent(
        db,
        current_user,
        uuid,
    )

@router.patch(
    "/{uuid}",
    response_model=AgentRead,
)   
def update_agent(
    uuid: str,
    data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return agent_service.update_agent(
        db,
        current_user,
        uuid,
        data,
    )

@router.delete(
    "/{uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_agent(
    uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent_service.delete_agent(
        db,
        current_user,
        uuid,
    )