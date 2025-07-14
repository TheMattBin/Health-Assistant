import os
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

# Simple file-based chat history (per user) for demo
CHAT_HISTORY_DIR = "chat_history_db"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def get_user_id(request: Request) -> str:
    # For demo, use a fixed user or extract from JWT in production
    return "demo_user"

def get_history_path(user_id: str) -> str:
    return os.path.join(CHAT_HISTORY_DIR, f"{user_id}.json")

def load_history(user_id: str) -> List[Dict[str, Any]]:
    path = get_history_path(user_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(user_id: str, history: List[Dict[str, Any]]):
    path = get_history_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@router.get("/history", response_model=List[Dict[str, Any]])
def get_chat_history(request: Request):
    user_id = get_user_id(request)
    return load_history(user_id)

@router.post("/history")
def add_chat_message(request: Request, message: Dict[str, Any]):
    user_id = get_user_id(request)
    history = load_history(user_id)
    message["timestamp"] = datetime.utcnow().isoformat()
    history.append(message)
    save_history(user_id, history)
    return {"status": "ok"}
