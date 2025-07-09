from fastapi import APIRouter

router = APIRouter()

# Stub for file upload endpoints
@router.post("/")
def upload_file():
    return {"msg": "File upload endpoint (stub)"}
