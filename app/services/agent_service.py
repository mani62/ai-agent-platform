from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.schemas.agent import AgentCreate, AgentUpdate
from app.models.agent import Agent


class AgentService:
    def __init__(self):
        self.agent_repository = AgentRepository()

    def create(
        self,
        db: Session,
        data: AgentCreate,
        current_user: User,
    ) -> Agent:
        agent = Agent(
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            model=data.model
        )

        return self.agent_repository.create(
            db,
            agent
        )
    
    def get_my_agents(
        self,
        db: Session,
        current_user: User,
    ):
        return self.agent_repository.get_all_by_user(
            db,
            current_user.id,
        )
    
    def get_agent(
        self,
        db: Session,
        current_user: User,
        uuid: str,
    ) -> Agent:

        agent = self.agent_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        return agent
    
    def update_agent(
        self,
        db: Session,
        current_user: User,
        uuid: str,
        data: AgentUpdate,
    ) -> Agent:
        agent = self.agent_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(agent, field, value)

        return self.agent_repository.save(
            db,
            agent,
        )
    
    def delete_agent(
        self,
        db: Session,
        current_user: User,
        uuid: str,
    ) -> None:
        agent = self.agent_repository.get_by_uuid_and_user(
            db,
            uuid,
            current_user.id,
        )

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found",
            )

        self.agent_repository.soft_delete(
            db,
            agent,
        )

    