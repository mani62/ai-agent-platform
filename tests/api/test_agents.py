from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.agent import Agent
from app.models.user import User

# Create Agent Scenarios
def test_create_agent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Research Assistant",
        "description": "Helps with research tasks",
        "system_prompt": "You are an expert research assistant.",
        "model": "gpt-4.1-mini",
    }

    response = client.post(
        "/agents",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["system_prompt"] == payload["system_prompt"]
    assert data["model"] == payload["model"]

    assert data["is_active"] is True

    assert "uuid" in data

def test_create_agent_without_authentication(
    client: TestClient,
) -> None:
    payload = {
        "name": "Research Assistant",
        "description": "Helps with research tasks",
        "system_prompt": "You are an expert research assistant.",
        "model": "gpt-4.1-mini",
    }

    response = client.post(
        "/agents",
        json=payload,
    )

    assert response.status_code == 401   

def test_create_agent_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
) -> None:
    payload = {
        "name": "Coding Assistant",
        "description": "Helps with programming tasks",
        "system_prompt": "You are an expert software engineer.",
        "model": "gpt-4.1-mini",
    }

    response = client.post(
        "/agents",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    response_data = response.json()

    agent = (
        db.query(Agent)
        .filter(
            Agent.uuid == response_data["uuid"],
        )
        .first()
    )

    assert agent is not None

    assert agent.name == payload["name"]

    assert agent.deleted_at is None     

# Get Agent Scenarios
def test_get_my_agents(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    response = client.get(
        "/agents",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["uuid"] == test_agent.uuid
    assert data[0]["name"] == test_agent.name
    assert data[0]["is_active"] is False

def test_get_agent_by_uuid(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    response = client.get(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["uuid"] == test_agent.uuid
    assert data["name"] == test_agent.name
    assert data["description"] == test_agent.description
    assert data["system_prompt"] == test_agent.system_prompt
    assert data["model"] == test_agent.model
    assert data["is_active"] is False

def test_get_agent_with_invalid_uuid(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/agents/{invalid_uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Agent not found",
    }

def test_user_cannot_access_another_users_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
) -> None:
    agent = Agent(
        user_id=second_user.id,
        name="Private Agent",
        description="Second user's agent",
        system_prompt="Private instructions",
        model="gpt-4.1-mini",
        is_active=False,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    response = client.get(
        f"/agents/{agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404    

def test_get_soft_deleted_agent_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    test_agent.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(test_agent)

    response = client.get(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_soft_deleted_agent_not_in_agents_list(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    test_agent.deleted_at = datetime.now(timezone.utc)

    db.commit()

    response = client.get(
        "/agents",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []  

def test_soft_deleted_agent_not_in_agents_list(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    test_agent.deleted_at = datetime.now(timezone.utc)

    db.commit()

    response = client.get(
        "/agents",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []

# Update Agent Scenarios
def test_partial_update_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    original_description = test_agent.description
    original_system_prompt = test_agent.system_prompt
    original_model = test_agent.model

    payload = {
        "name": "Only Name Changed",
    }

    response = client.patch(
        f"/agents/{test_agent.uuid}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == payload["name"]

    assert data["description"] == original_description

    assert data["system_prompt"] == original_system_prompt

    assert data["model"] == original_model

def test_update_agent_persists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    payload = {
        "name": "Database Updated Agent",
    }

    response = client.patch(
        f"/agents/{test_agent.uuid}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200

    db.refresh(test_agent)

    assert test_agent.name == payload["name"]

def test_update_nonexistent_agent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.patch(
        f"/agents/{invalid_uuid}",
        json={
            "name": "Updated Agent",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Agent not found",
    }

def test_user_cannot_update_another_users_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
) -> None:
    agent = Agent(
        user_id=second_user.id,
        name="Private Agent",
        description="Private description",
        system_prompt="Private instructions",
        model="gpt-4.1-mini",
        is_active=False,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    response = client.patch(
        f"/agents/{agent.uuid}",
        json={
            "name": "Hacked Agent",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    db.refresh(agent)

    assert agent.name == "Private Agent"

def test_cannot_update_soft_deleted_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    test_agent.deleted_at = datetime.now(timezone.utc)

    db.commit()

    response = client.patch(
        f"/agents/{test_agent.uuid}",
        json={
            "name": "Updated Deleted Agent",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404

    db.refresh(test_agent)

    assert test_agent.name == "Test Agent"

def test_activate_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    assert test_agent.is_active is False

    response = client.patch(
        f"/agents/{test_agent.uuid}",
        json={
            "is_active": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_active"] is True

def test_update_agent_description_to_null(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    assert test_agent.description is not None

    response = client.patch(
        f"/agents/{test_agent.uuid}",
        json={
            "description": None,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["description"] is None   

# Soft Delete Agent Scenarios
def test_soft_delete_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""

    db.refresh(test_agent)

    assert test_agent.deleted_at is not None

def test_soft_deleted_agent_still_exists_in_database(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    test_agent: Agent,
) -> None:
    agent_id = test_agent.id

    response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    agent_in_database = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    assert agent_in_database is not None
    assert agent_in_database.deleted_at is not None

def test_soft_deleted_agent_not_returned_in_list(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    delete_response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    list_response = client.get(
        "/agents",
        headers=auth_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []

def test_soft_deleted_agent_cannot_be_retrieved(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    delete_response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404

    assert get_response.json() == {
        "detail": "Agent not found",
    }

def test_user_cannot_delete_another_users_agent(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
    second_user: User,
) -> None:
    other_agent = Agent(
        user_id=second_user.id,
        name="Second User Agent",
        description="Private agent",
        system_prompt="Private prompt",
        model="gpt-4.1-mini",
        is_active=False,
    )

    db.add(other_agent)
    db.commit()
    db.refresh(other_agent)

    response = client.delete(
        f"/agents/{other_agent.uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

    db.refresh(other_agent)

    assert other_agent.deleted_at is None

def test_delete_nonexistent_agent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    invalid_uuid = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/agents/{invalid_uuid}",
        headers=auth_headers,
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Agent not found",
    }

def test_delete_agent_twice_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
    test_agent: Agent,
) -> None:
    first_response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert first_response.status_code == 204

    second_response = client.delete(
        f"/agents/{test_agent.uuid}",
        headers=auth_headers,
    )

    assert second_response.status_code == 404

    assert second_response.json() == {
        "detail": "Agent not found",
    }

def test_delete_agent_without_authentication(
    client: TestClient,
    test_agent: Agent,
) -> None:
    response = client.delete(
        f"/agents/{test_agent.uuid}",
    )

    assert response.status_code == 401
                                