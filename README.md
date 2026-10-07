# AI Agent Platform

Backend API for creating personal AI agents, attaching tools, and chatting with them. Each user owns their agents and conversations. A message is answered by the agent bound to that chat, which can call allowed tools before it replies.

The service is a [FastAPI](https://fastapi.tiangolo.com/ "https://fastapi.tiangolo.com/") application backed by PostgreSQL. Language models are reached through a provider interface. [Ollama](https://ollama.com/ "https://ollama.com/") is the implemented provider.

## Features

- User registration and JWT authentication
- Per-user agents with a name, description, system prompt, provider, and model
- Tool allow-lists so an agent can only call tools assigned to it
- Chats scoped to a single agent, with titles generated from the first message
- A tool-calling loop that runs the model, executes tool calls, and feeds results back
- Built-in calculator tool, with a registry for adding more
- Interactive API docs at `/docs`

## Tech Stack

- Python 3.13 and FastAPI
- SQLAlchemy and Alembic
- PostgreSQL
- Pydantic
- Ollama for local LLM inference
- Docker and Docker Compose
- Pytest

## Architecture

Requests enter through FastAPI routers, pass through services, and persist through repositories and SQLAlchemy models. Agent execution is decoupled from the HTTP layer:

| Layer              | Responsibility                                               |
| :----------------- | :----------------------------------------------------------- |
| `app/api`          | HTTP routes, auth dependencies, request and response schemas |
| `app/services`     | Business rules for users, agents, chats, and messages        |
| `app/repositories` | Database access                                              |
| `app/ai`           | Agent runner, prompts, and tools                             |
| `app/llm`          | Provider interface, factory, and Ollama client               |
| `app/models`       | SQLAlchemy models                                            |

When a user sends a message, the platform stores it, loads the chat history, and runs the agent. The runner calls the model with the agent's system prompt and only the tools assigned to that agent. If the model requests a tool, the runner executes it and continues, up to five iterations. The final text is stored as the assistant message. On the first message in a chat, a short title is generated from that message.

## How it works

```text
User -> API -> Chat/Message Services -> Agent Runner -> LLM Provider
                                           |
                                           v
                                      Allowed Tools
                                           |
                                           v
                                      Final Response
```


## Requirements

- Python 3.13
- PostgreSQL 17 (recommended)
- [Ollama](https://ollama.com/ "https://ollama.com/") running locally, with a tool-capable model pulled (for example `llama3.1`)
- Docker and Docker Compose, if you run the stack in containers

## Quick start with Docker

1. Create an environment file and set a real secret:

```bash
cp .env.example .env

```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env

```

2. Point the API at the Compose database. Inside the API container the database host is `db`:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/ai_agent_db
SECRET_KEY=replace-with-a-long-random-string

```

3. If Ollama runs on the host machine, the container cannot reach it at `localhost`. Use the host gateway:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434

```

4. Start the services. The API is published on port **9000**:

```bash
docker compose up --build

```

5. Apply migrations from the API container:

```bash
docker compose exec api alembic upgrade head

```

6. Open [http://localhost:9000/docs](http://localhost:9000/docs "http://localhost:9000/docs"). A healthy service also responds at [http://localhost:9000/health](http://localhost:9000/health "http://localhost:9000/health").

Pull a model before chatting, for example:

```bash
ollama pull llama3.1

```

## Local development

Use this when you want to run the API on the host and PostgreSQL in Docker, or against any local Postgres instance.

```bash
python -m venv .venv

```

Activate the virtual environment, then install dependencies:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

```

Set `DATABASE_URL` to a host-reachable Postgres URL, for example `postgresql://postgres:postgres@localhost:5432/ai_agent_db`, and set `OLLAMA_BASE_URL=http://localhost:11434`.

```bash
alembic upgrade head
uvicorn app.main:app --reload

```

The API listens on [http://127.0.0.1:8000](http://127.0.0.1:8000/ "http://127.0.0.1:8000"). Docs are at `/docs`.

## Configuration

Settings are loaded from `.env`. See `.env.example`.

| Variable                      | Purpose                                     |
| :---------------------------- | :------------------------------------------ |
| `APP_NAME`                    | Application title shown in the OpenAPI docs |
| `DATABASE_URL`                | SQLAlchemy connection URL                   |
| `SECRET_KEY`                  | Secret used to sign access tokens           |
| `ALGORITHM`                   | JWT signing algorithm (`HS256`)             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime                       |
| `OLLAMA_BASE_URL`             | Base URL of the Ollama server               |

Change `SECRET_KEY` before any shared or deployed use.

## API

All routes except registration, login, `/`, and `/health` require `Authorization: Bearer <access_token>`.

| Method   | Path                          | Description                                    |
| :------- | :---------------------------- | :--------------------------------------------- |
| `POST`   | `/auth/register`              | Create a user                                  |
| `POST`   | `/auth/login`                 | Issue an access token                          |
| `GET`    | `/users/me`                   | Current user                                   |
| `POST`   | `/agents`                     | Create an agent                                |
| `GET`    | `/agents`                     | List the current user's agents                 |
| `GET`    | `/agents/{uuid}`              | Get one agent                                  |
| `PATCH`  | `/agents/{uuid}`              | Update an agent                                |
| `DELETE` | `/agents/{uuid}`              | Delete an agent                                |
| `POST`   | `/chats`                      | Start a chat with an agent                     |
| `GET`    | `/chats`                      | List the current user's chats                  |
| `GET`    | `/chats/{uuid}`               | Get one chat                                   |
| `PATCH`  | `/chats/{uuid}`               | Rename a chat                                  |
| `DELETE` | `/chats/{uuid}`               | Delete a chat                                  |
| `POST`   | `/chats/{chat_uuid}/messages` | Send a message and receive the assistant reply |
| `GET`    | `/chats/{chat_uuid}/messages` | List messages in a chat                        |

Login uses the OAuth2 password form. Send the email in the `username` field:

```bash
curl -X POST http://localhost:9000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ada@example.com&password=your-password"

```

Register a user:

```bash
curl -X POST http://localhost:9000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "password": "your-password"
  }'

```

Create an agent. `provider` must be `ollama`. `model` must be a model available to that Ollama server. `tool_uuids` is optional; see [Tools](#tools).

```bash
curl -X POST http://localhost:9000/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analyst",
    "description": "Answers questions and can calculate.",
    "system_prompt": "You are a careful assistant. Use tools when arithmetic is required.",
    "provider": "ollama",
    "model": "llama3.1",
    "tool_uuids": []
  }'

```

Start a chat, then send a message. The response body is the assistant message. The user message is stored in the same chat.

```bash
curl -X POST http://localhost:9000/chats \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_uuid": "<agent-uuid>"}'

curl -X POST http://localhost:9000/chats/<chat-uuid>/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is 25 * 4 + 10?"}'

```

Replace port `9000` with `8000` when the API is running directly with Uvicorn.

## Tools

Tools are Python classes that implement `BaseTool` in `app/ai/tools`. Each tool exposes a name, description, JSON schema, and an `execute` method. `register_tools()` in `app/ai/tools/setup.py` registers them at startup, and `ToolService` syncs those definitions into the `tools` table.

The built-in tool is `calculator`. It evaluates arithmetic expressions (`+`, `-`, `*`, `/`, `**`, `%`) without using Python `eval`.

After the API has started once, look up tool UUIDs and pass them in `tool_uuids` when creating or updating an agent:

```sql
SELECT uuid, name, description FROM tools;

```

An agent never sees tools that are not on its allow-list. Unknown or disallowed tool calls are returned to the model as an error string.

To add a tool, subclass `BaseTool`, register an instance in `register_tools()`, and restart the API so the database row is created.

## Tests

Tests use an in-memory SQLite database and do not call Ollama. The test suite covers API behaviour, persistence, message flows, and agent/tool execution without requiring a live LLM server.

```bash
pytest

```

## Project layout

```text
app/
  api/            HTTP routers
  services/       Application services
  repositories/   Data access
  models/         SQLAlchemy models
  schemas/        Pydantic request and response models
  ai/             Agent runner, prompts, and tools
  llm/            LLM provider interface and Ollama client
  core/           Settings and security helpers
  db/             Engine, session, and model mixins
alembic/          Database migrations
tests/            API and tool tests
docker-compose.yml
Dockerfile
```