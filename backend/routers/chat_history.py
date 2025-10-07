import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from jose import JWTError, jwt

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/oauth2/login/google")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

CHAT_HISTORY_DIR = "chat_history_db"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

class ChatMessage(BaseModel):
    sender: str
    text: str
    fileName: Optional[str] = None
    timestamp: Optional[str] = None

class ChatSession(BaseModel):
    id: str
    title: str
    created_at: str
    messages: List[ChatMessage]

def get_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_history_path(user_id: str) -> str:
    return os.path.join(CHAT_HISTORY_DIR, f"{user_id}.json")

def load_sessions(user_id: str) -> List[Dict[str, Any]]:
    path = get_history_path(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_sessions(user_id: str, sessions: List[Dict[str, Any]]):
    path = get_history_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def get_session_by_id(user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    sessions = load_sessions(user_id)
    for session in sessions:
        if session["id"] == session_id:
            return session
    return None

@router.get("/sessions", response_model=List[Dict[str, Any]])
def get_chat_sessions(user_id: str = Depends(get_user_id)):
    sessions = load_sessions(user_id)
    return [
        {
            "id": session["id"],
            "title": session["title"],
            "created_at": session["created_at"]
        }
        for session in sessions
    ]

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
def get_chat_session(session_id: str, user_id: str = Depends(get_user_id)):
    session = get_session_by_id(user_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/sessions")
def create_chat_session(session_data: Dict[str, str], user_id: str = Depends(get_user_id)):
    sessions = load_sessions(user_id)

    new_session = {
        "id": f"session_{datetime.utcnow().timestamp()}",
        "title": session_data.get("title", "New Chat"),
        "created_at": datetime.utcnow().isoformat(),
        "messages": []
    }

    sessions.append(new_session)
    save_sessions(user_id, sessions)
    return {"session_id": new_session["id"]}

@router.post("/sessions/{session_id}/messages")
def add_message_to_session(session_id: str, message: ChatMessage, user_id: str = Depends(get_user_id)):
    sessions = load_sessions(user_id)

    session_index = -1
    for i, session in enumerate(sessions):
        if session["id"] == session_id:
            session_index = i
            break

    if session_index == -1:
        raise HTTPException(status_code=404, detail="Session not found")

    if not message.timestamp:
        message.timestamp = datetime.utcnow().isoformat()

    sessions[session_index]["messages"].append(message.dict())
    save_sessions(user_id, sessions)

    return {"status": "ok"}

@router.get("/history", response_model=List[Dict[str, Any]])
def get_chat_history_legacy(user_id: str = Depends(get_user_id)):
    sessions = load_sessions(user_id)
    all_messages = []
    for session in sessions:
        for message in session.get("messages", []):
            all_messages.append(message)
    return all_messages

@router.post("/history")
def add_chat_message_legacy(message: Dict[str, Any], user_id: str = Depends(get_user_id)):
    sessions = load_sessions(user_id)

    if not sessions:
        new_session = {
            "id": f"session_{datetime.utcnow().timestamp()}",
            "title": "Legacy Chat",
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        sessions.append(new_session)

    message["timestamp"] = datetime.utcnow().isoformat()
    sessions[-1]["messages"].append(message)
    save_sessions(user_id, sessions)

    return {"status": "ok"}
