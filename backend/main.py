from fastapi import FastAPI
from routers import auth, health_data, chat, file_upload, model_api

app = FastAPI(title="OpenHealth-Inspired AI Health Assistant")

# Modular routers
app.include_router(auth.router, prefix="/auth")
app.include_router(health_data.router, prefix="/health")
app.include_router(chat.router, prefix="/chat")
app.include_router(file_upload.router, prefix="/upload")
app.include_router(model_api.router, prefix="/model")
