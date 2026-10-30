import os

from dotenv import load_dotenv

# Routers read SECRET_KEY etc. at import time, so .env must be loaded first.
load_dotenv()

from fastapi import FastAPI
from routers import auth, chat, chat_history, oauth2
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from utils.file_storage import UPLOADS_DIR, USERS_DIR

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

# Serve uploaded files (StaticFiles refuses to mount a missing directory)
os.makedirs(USERS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(auth.router, prefix="/auth")
app.include_router(oauth2.router, prefix="/auth/oauth2")
app.include_router(chat.router, prefix="/chat")
app.include_router(chat_history.router, prefix="/chat")


@app.get("/health")
def health():
    return {"status": "ok"}
