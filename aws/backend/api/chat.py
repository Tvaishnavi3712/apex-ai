"""
Chat API endpoints
Work Room chat interface for conversational agents
"""

from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import json

from services.dynamodb import DynamoDBService
from services.agentcore import AgentCoreService
from core.config import settings

router = APIRouter()
db = DynamoDBService(settings.DYNAMODB_SESSIONS)
agentcore = AgentCoreService()


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


@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, content: str, attachments: List[str] = None):
    """Send a message in a session (HTTP fallback for non-WebSocket)"""
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

    # Invoke AgentCore agent
    agent_id = session.get("agent_id", "invoice-bot")
    agent_result = await agentcore.invoke_agent(agent_id, content)

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
            # 1. Invoke AgentCore with streaming
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


@router.post("/invoke/{agent_id}")
async def invoke_agent(agent_id: str, prompt: str):
    """
    Direct agent invocation without session management.
    Useful for simple queries and demos.
    """
    result = await agentcore.invoke_agent(agent_id, prompt)

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
        "agents": agentcore.get_available_agents()
    }
