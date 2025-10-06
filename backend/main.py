from fastapi import FastAPI
from routers import auth, health_data, chat, file_upload, model_api, chat_history, oauth2
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI(title="OpenHealth-Inspired AI Health Assistant")

# Add session middleware (required for OAuth2)
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-in-production"  # In production, use a secure secret key
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modular routers
app.include_router(auth.router, prefix="/auth")
app.include_router(oauth2.router, prefix="/auth/oauth2")
# app.include_router(health_data.router, prefix="/health")
app.include_router(chat.router, prefix="/chat")
# app.include_router(file_upload.router, prefix="/upload")
# app.include_router(model_api.router, prefix="/model")
app.include_router(chat_history.router, prefix="/chat")
