from fastapi import APIRouter

router = APIRouter()

# Stub for authentication endpoints
@router.post("/login")
def login():
    return {"msg": "Login endpoint (stub)"}
