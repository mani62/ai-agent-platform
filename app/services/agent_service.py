from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tool import Tool
from app.models.user import User
from app.repositories.agent_repository import AgentRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.agent import AgentCreate, AgentUpdate
from app.models.agent import Agent


class AgentService:
    def __init__(self):
        self.agent_repository = AgentRepository()
        self.tool_repository = ToolRepository()

    def create(
        self,
        db: Session,
        data: AgentCreate,
        current_user: User,
    ) -> Agent:
        tools = self._resolve_tools(
            db,
            data.tool_uuids,
        )
            
        agent = Agent(
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            provider=data.provider,
            model=data.model,
            tools=tools,
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

        tool_uuids = update_data.pop(
            "tool_uuids",
            None,
        )
        
        for field, value in update_data.items():
            setattr(agent, field, value)

        if tool_uuids is not None:
            agent.tools = self._resolve_tools(
                db,
                tool_uuids,
            )    

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

    def _resolve_tools(
        self,
        db: Session,
        tool_uuids: list[UUID],
    ) -> list[Tool]:
        if not tool_uuids:
            return []

        unique_uuids = list(set(tool_uuids))

        if len(unique_uuids) != len(tool_uuids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate tools are not allowed",
            )

        tools = self.tool_repository.get_by_uuids(
            db,
            [str(uuid) for uuid in tool_uuids],
        )

        if len(tools) != len(tool_uuids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tools were not found",
            )

        return tools    

    