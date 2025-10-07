from fastapi import FastAPI
from routers import auth, health_data, chat, file_upload, model_api, chat_history, oauth2
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="OpenHealth-Inspired AI Health Assistant")

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(oauth2.router, prefix="/auth/oauth2")
app.include_router(chat.router, prefix="/chat")
app.include_router(chat_history.router, prefix="/chat")
