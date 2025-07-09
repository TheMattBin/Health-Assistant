from fastapi import APIRouter

router = APIRouter()

# Stub for health data endpoints
@router.get("/")
def get_health_data():
    return {"msg": "Health data endpoint (stub)"}
