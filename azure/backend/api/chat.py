"""
Chat API endpoints
Work Room chat interface for conversational agents
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import json

from services.cosmos import CosmosService
from services.foundry_agent import FoundryAgentService
from core.config import settings

router = APIRouter()
db = CosmosService(settings.TABLE_SESSIONS)
foundry_agent = FoundryAgentService()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@router.post("/sessions")
async def create_session(agent_id: str, user_id: str = "anonymous"):
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    session_data = {
        "session_id": session_id,
        "agent_id": agent_id,
        "user_id": user_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": "active",
        "messages": []
    }

    await db.put_item(session_data)

    return {
        "session_id": session_id,
        "agent_id": agent_id,
        "status": "active"
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details and message history"""
    session = await db.get_item({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return session


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50):
    """Get messages for a session"""
    session = await db.get_item({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    messages = session.get("messages", [])
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages[-limit:]
    }


@router.get("/sessions/{session_id}/messages/{message_id}/dvr")
async def get_message_dvr(session_id: str, message_id: str):
    """Killer Feature 2 — Audit Lens.

    Returns the reasoning + actions_taken that the agent generated for a
    specific assistant message. The data is whatever the Foundry Agent Service runtime
    (or its local fallback) returned — we do NOT synthesize steps here.
    If the message exists but has no reasoning, steps=[] is returned so the
    UI can display 'no trace' rather than fabricate one.
    """
    session = await db.get_item({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")

    messages = session.get("messages", [])
    target = next((m for m in messages if m.get("message_id") == message_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Message {message_id} not found in session {session_id}")

    # Context: what was the user asking + when?
    idx = messages.index(target)
    user_turn = None
    for prior in reversed(messages[:idx]):
        if prior.get("role") == "user":
            user_turn = prior
            break

    return {
        "session_id": session_id,
        "message_id": message_id,
        "agent_id":   session.get("agent_id"),
        "asked_at":   user_turn.get("timestamp") if user_turn else None,
        "asked":      user_turn.get("content")   if user_turn else None,
        "answered_at": target.get("timestamp"),
        "reasoning":   target.get("reasoning", []),
        "actions_taken": target.get("actions_taken", []),
        "model":      target.get("model")  or "us.amazon.nova-pro-v1:0",
    }


class SendMessageBody(BaseModel):
    """Optional JSON body for /messages — carries multi-LLM overrides.

    The frontend's Settings → AgentModelsPanel persists per-browser model
    overrides; agent-hub.tsx attaches them here so the backend can forward
    to the Foundry Agent Service runtime payload.
    """
    model_overrides: Optional[Dict[str, Dict[str, str]]] = None
    attachments: Optional[List[str]] = None


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    content: str,
    body: Optional[SendMessageBody] = None,
):
    """Send a message in a session (HTTP fallback for non-WebSocket).

    Body fields (all optional):
      • model_overrides — {agent_id: {slot_key: model_id}} for per-tier LLM swap
      • attachments     — list of blob URIs / file ids
    """
    body = body or SendMessageBody()
    attachments = body.attachments or []
    model_overrides = body.model_overrides
    session = await db.get_item({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    now = datetime.utcnow()
    message_id = str(uuid.uuid4())

    user_message = {
        "message_id": message_id,
        "role": "user",
        "content": content,
        "attachments": attachments or [],
        "timestamp": now.isoformat()
    }

    # Add user message to session
    messages = session.get("messages", [])
    messages.append(user_message)

    # Invoke Foundry Agent Service agent
    # Look up agent to get name for routing (sessions store UUID)
    agent_id = session.get("agent_id", "invoice-bot")
    agents_db = CosmosService(settings.TABLE_AGENTS)
    agent = await agents_db.get_item({"agent_id": agent_id})
    agent_name = agent.get("name", agent_id) if agent else agent_id

    # Conversation history: every turn that came BEFORE the user message we
    # just appended. Passing this to invoke_agent is what makes follow-up
    # questions work — without it, the agent sees each message in isolation
    # and forgets everything said previously.
    #
    # We only forward role+content pairs, and cap at the most recent 12 turns
    # so the Foundry Agent Service payload stays comfortably under the 100KB CLI limit.
    recent_turns = [
        {"role": m.get("role"), "content": m.get("content", "")}
        for m in messages[:-1]                             # exclude the user msg we just added
        if m.get("role") in ("user", "assistant") and m.get("content")
    ][-12:]

    agent_result = await foundry_agent.invoke_agent(
        agent_name,
        content,
        session_id=session_id,
        history=recent_turns,
        model_overrides=model_overrides,
    )

    if agent_result["success"]:
        agent_message = {
            "message_id": str(uuid.uuid4()),
            "role": "assistant",
            "content": agent_result["response"],
            "reasoning": agent_result.get("reasoning", []),
            "actions_taken": agent_result.get("actions_taken", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        agent_message = {
            "message_id": str(uuid.uuid4()),
            "role": "assistant",
            "content": f"I apologize, I encountered an issue processing your request. Error: {agent_result.get('error', 'Unknown error')}",
            "reasoning": [],
            "actions_taken": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    messages.append(agent_message)

    # Update session
    await db.update_item(
        {"session_id": session_id},
        {
            "messages": messages,
            "updated_at": now.isoformat()
        }
    )

    return {
        "user_message": user_message,
        "agent_response": agent_message
    }


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    # Verify session exists
    session = await db.get_item({"session_id": session_id})
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            now = datetime.utcnow()
            message_id = str(uuid.uuid4())

            # Create user message
            user_message = {
                "message_id": message_id,
                "role": "user",
                "content": message_data.get("content", ""),
                "attachments": message_data.get("attachments", []),
                "timestamp": now.isoformat()
            }

            # Send acknowledgment
            await manager.send_message(session_id, {
                "type": "message_received",
                "message": user_message
            })

            # TODO: Stream agent response
            # 1. Invoke Foundry Agent Service with streaming
            # 2. Send reasoning steps as they happen
            # 3. Send final response

            # Send thinking indicator
            await manager.send_message(session_id, {
                "type": "agent_thinking",
                "message": "Processing your request..."
            })

            # Placeholder response
            agent_message = {
                "message_id": str(uuid.uuid4()),
                "role": "assistant",
                "content": f"I received: {message_data.get('content', '')}",
                "reasoning": [
                    {"step": 1, "thought": "Analyzing user request..."},
                    {"step": 2, "thought": "Determining appropriate action..."}
                ],
                "actions_taken": [],
                "timestamp": datetime.utcnow().isoformat()
            }

            await manager.send_message(session_id, {
                "type": "agent_response",
                "message": agent_message
            })

            # Update session in DB
            session = await db.get_item({"session_id": session_id})
            messages = session.get("messages", [])
            messages.extend([user_message, agent_message])
            await db.update_item(
                {"session_id": session_id},
                {"messages": messages, "updated_at": now.isoformat()}
            )

    except WebSocketDisconnect:
        manager.disconnect(session_id)


@router.delete("/sessions/{session_id}")
async def end_session(session_id: str):
    """End a chat session"""
    session = await db.get_item({"session_id": session_id})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    await db.update_item(
        {"session_id": session_id},
        {
            "status": "ended",
            "ended_at": datetime.utcnow().isoformat()
        }
    )

    manager.disconnect(session_id)

    return {"session_id": session_id, "status": "ended"}


class InvokeAgentBody(BaseModel):
    """Optional body for /invoke/{agent_id} carrying multi-LLM overrides."""
    model_overrides: Optional[Dict[str, Dict[str, str]]] = None


@router.post("/invoke/{agent_id}")
async def invoke_agent(
    agent_id: str,
    prompt: str,
    body: Optional[InvokeAgentBody] = None,
):
    """
    Direct agent invocation without session management.
    Useful for simple queries and demos.

    Optional body field `model_overrides` lets callers pin specific
    Azure OpenAI models per (agent, slot). Backend forwards to the Foundry Agent Service
    runtime payload so each agent can pick the right AzureOpenAIModel.
    """
    # Look up agent by ID to get the agent name for routing
    # Frontend passes UUID but routing logic needs agent name/type
    agents_db = CosmosService(settings.TABLE_AGENTS)
    agent = await agents_db.get_item({"agent_id": agent_id})

    # Use agent name for invocation if found, otherwise use the ID as-is
    agent_name = agent.get("name", agent_id) if agent else agent_id

    model_overrides = (body or InvokeAgentBody()).model_overrides
    result = await foundry_agent.invoke_agent(
        agent_name, prompt, model_overrides=model_overrides,
    )

    if result["success"]:
        return {
            "agent_id": agent_id,
            "prompt": prompt,
            "response": result["response"],
            "reasoning": result.get("reasoning", []),
            "actions_taken": result.get("actions_taken", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Agent invocation failed")
        )


@router.get("/agents")
async def list_agents():
    """Get list of available agents."""
    return {
        "agents": foundry_agent.get_available_agents()
    }
