from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.user import User
from app.models.agent import Agent

def test_create_chat_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
    test_user: User,
    db: Session,
) -> None:

    response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    chat = (
        db.query(Chat)
        .filter(Chat.uuid == data["uuid"])
        .first()
    )

    assert chat is not None
    assert "uuid" in data
    assert chat.title is None