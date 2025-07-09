from fastapi import APIRouter

router = APIRouter()

# Stub for chat endpoints
@router.post("/ask")
def ask():
    return {"msg": "Chat endpoint (stub)"}
