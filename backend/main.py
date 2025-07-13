from fastapi import FastAPI
from routers import auth
#, health_data, chat, file_upload, model_api
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="OpenHealth-Inspired AI Health Assistant")

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
# app.include_router(health_data.router, prefix="/health")
# app.include_router(chat.router, prefix="/chat")
# app.include_router(file_upload.router, prefix="/upload")
# app.include_router(model_api.router, prefix="/model")
