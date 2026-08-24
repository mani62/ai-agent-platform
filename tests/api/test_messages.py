from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.chat import Chat
from app.models.message import Message
from app.models.user import User

# Create Message
def test_create_message(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    assert chat_response.status_code == 201

    chat_uuid = chat_response.json()["uuid"]

    response = client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Explain FastAPI dependencies",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["content"] == "Explain FastAPI dependencies"
    assert data["role"] == "user"
    assert "uuid" in data

def test_create_message_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
    db: Session,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    response = client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Hello Agent",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    message_uuid = response.json()["uuid"]

    message = (
        db.query(Message)
        .filter(Message.uuid == message_uuid)
        .first()
    )

    assert message is not None
    assert message.content == "Hello Agent"
    assert message.role == "user"

def test_message_belongs_to_correct_chat(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
    db: Session,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    chat = (
        db.query(Chat)
        .filter(Chat.uuid == chat_uuid)
        .first()
    )

    response = client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Test message",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    message = (
        db.query(Message)
        .filter(
            Message.uuid == response.json()["uuid"]
        )
        .first()
    )

    assert message is not None
    assert message.chat_id == chat.id

# Get Messages
def test_get_chat_messages(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "First message",
        },
        headers=auth_headers,
    )

    client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Second message",
        },
        headers=auth_headers,
    )

    response = client.get(
        f"/chats/{chat_uuid}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["content"] == "First message"
    assert data[1]["content"] == "Second message"
    
def test_get_messages_returns_empty_list(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    response = client.get(
        f"/chats/{chat_uuid}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []

def test_cannot_create_message_for_nonexistent_chat(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        f"/chats/{invalid_uuid}/messages",
        json={
            "content": "Hello",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Chat not found",
    }

def test_get_messages_for_nonexistent_chat(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/chats/{invalid_uuid}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Chat not found",
    }

def test_cannot_create_message_in_another_users_chat(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
    active_agent: Agent,
) -> None:

    other_chat = Chat(
        user_id=second_user.id,
        agent_id=active_agent.id,
        title="Private Chat",
    )

    db.add(other_chat)
    db.commit()
    db.refresh(other_chat)

    response = client.post(
        f"/chats/{other_chat.uuid}/messages",
        json={
            "content": "Trying to access another chat",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_cannot_get_another_users_messages(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
    active_agent: Agent,
) -> None:

    other_chat = Chat(
        user_id=second_user.id,
        agent_id=active_agent.id,
        title="Private Chat",
    )

    db.add(other_chat)
    db.commit()
    db.refresh(other_chat)

    message = Message(
        chat_id=other_chat.id,
        role="user",
        content="Private message",
    )

    db.add(message)
    db.commit()

    response = client.get(
        f"/chats/{other_chat.uuid}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_cannot_create_message_for_deleted_chat(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    delete_response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    response = client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Hello",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_create_message_without_authentication(
    client: TestClient,
    active_agent: Agent,
    auth_headers: dict[str, str],
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    response = client.post(
        f"/chats/{chat_uuid}/messages",
        json={
            "content": "Hello",
        },
    )

    assert response.status_code == 401

def test_get_messages_without_authentication(
    client: TestClient,
    active_agent: Agent,
    auth_headers: dict[str, str],
) -> None:

    chat_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = chat_response.json()["uuid"]

    response = client.get(
        f"/chats/{chat_uuid}/messages",
    )

    assert response.status_code == 401