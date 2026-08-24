from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.chat import Chat
from app.models.user import User

# Create Chat
def test_create_chat(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    payload = {
        "agent_uuid": active_agent.uuid,
    }

    response = client.post(
        "/chats",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert "uuid" in data
    assert data["title"] is None

    assert "id" not in data
    assert "user_id" not in data
    assert "agent_id" not in data

def test_create_chat_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
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

    assert "id" not in data
    assert "user_id" not in data
    assert "agent_id" not in data

def test_cannot_create_chat_with_inactive_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:

    response = client.post(
        "/chats",
        json={
            "agent_uuid": test_agent.uuid,
        },
        headers=auth_headers,
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Agent is inactive",
    }

def test_cannot_create_chat_with_nonexistent_agent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        "/chats",
        json={
            "agent_uuid": invalid_uuid,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Agent not found",
    }

def test_user_cannot_create_chat_with_another_users_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
) -> None:

    other_agent = Agent(
        user_id=second_user.id,
        name="Private Agent",
        description="Second user's agent",
        system_prompt="Private instructions",
        model="gpt-4.1-mini",
        is_active=True,
    )

    db.add(other_agent)
    db.commit()
    db.refresh(other_agent)

    response = client.post(
        "/chats",
        json={
            "agent_uuid": other_agent.uuid,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_create_chat_without_authentication(
    client: TestClient,
    active_agent: Agent,
) -> None:

    response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
    )

    assert response.status_code == 401                

# Get Chats
def test_get_my_chats_returns_empty_list(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    response = client.get(
        "/chats",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert response.json() == []

def test_get_my_chats_without_authentication(
    client: TestClient,
) -> None:

    response = client.get(
        "/chats",
    )

    assert response.status_code == 401   

def test_get_chat_by_uuid(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    created_chat = create_response.json()

    response = client.get(
        f"/chats/{created_chat['uuid']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["uuid"] == created_chat["uuid"]
    assert data["title"] is None         

def test_get_chat_with_invalid_uuid(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/chats/{invalid_uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Chat not found",
    }

def test_user_cannot_access_another_users_chat(
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

    response = client.get(
        f"/chats/{other_chat.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_get_chat_without_authentication(
    client: TestClient,
    active_agent: Agent,
    db: Session,
    test_user: User,
) -> None:

    chat = Chat(
        user_id=test_user.id,
        agent_id=active_agent.id,
        title=None,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    response = client.get(
        f"/chats/{chat.uuid}",
    )

    assert response.status_code == 401    

# Update Test
def test_update_chat_title(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    chat_uuid = create_response.json()["uuid"]

    response = client.patch(
        f"/chats/{chat_uuid}",
        json={
            "title": "FastAPI Questions",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["uuid"] == chat_uuid
    assert data["title"] == "FastAPI Questions"

def test_update_chat_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
    db: Session,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = create_response.json()["uuid"]

    response = client.patch(
        f"/chats/{chat_uuid}",
        json={
            "title": "Updated Chat",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    chat = (
        db.query(Chat)
        .filter(Chat.uuid == chat_uuid)
        .first()
    )

    assert chat is not None
    assert chat.title == "Updated Chat"

def test_update_nonexistent_chat(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:

    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.patch(
        f"/chats/{invalid_uuid}",
        json={
            "title": "Updated Chat",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Chat not found",
    }

# Soft Delete Chat
def test_soft_delete_chat(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
    db: Session,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    chat_uuid = create_response.json()["uuid"]

    response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    chat = (
        db.query(Chat)
        .filter(Chat.uuid == chat_uuid)
        .first()
    )

    assert chat is not None
    assert chat.deleted_at is not None

def test_soft_deleted_chat_cannot_be_retrieved(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = create_response.json()["uuid"]

    delete_response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404

    assert get_response.json() == {
        "detail": "Chat not found",
    }

def test_soft_deleted_chat_not_returned_in_list(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = create_response.json()["uuid"]

    delete_response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    response = client.get(
        "/chats",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []

def test_delete_chat_twice_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
    active_agent: Agent,
) -> None:

    create_response = client.post(
        "/chats",
        json={
            "agent_uuid": active_agent.uuid,
        },
        headers=auth_headers,
    )

    chat_uuid = create_response.json()["uuid"]

    first_response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert first_response.status_code == 204

    second_response = client.delete(
        f"/chats/{chat_uuid}",
        headers=auth_headers,
    )

    assert second_response.status_code == 404                
