from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional

router = APIRouter()

# Configuration
config = Config('.env')  # This will read from .env file
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# OAuth2 setup
oauth = OAuth(config)

# Configure Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Configure Facebook OAuth
oauth.register(
    name='facebook',
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/v18.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
    client_kwargs={
        'scope': 'email public_profile'
    },
    userinfo_endpoint='https://graph.facebook.com/me?fields=id,name,email,picture'
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = f"{BACKEND_URL}/auth/oauth2/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        # Create JWT token for our application
        access_token = create_access_token(
            data={
                "sub": user["email"],
                "name": user.get("name", ""),
                "picture": user.get("picture", ""),
                "provider": "google"
            }
        )

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth2 authentication failed: {str(e)}"
        )

@router.get("/login/facebook")
async def login_via_facebook(request: Request):
    redirect_uri = f"{BACKEND_URL}/auth/oauth2/facebook/callback"
    return await oauth.facebook.authorize_redirect(request, redirect_uri)

@router.get("/facebook/callback")
async def facebook_callback(request: Request):
    try:
        token = await oauth.facebook.authorize_access_token(request)

        # Get user info from Facebook Graph API
        resp = await oauth.facebook.get('me?fields=id,name,email,picture', token=token)
        user = resp.json()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Facebook"
            )

        # Create JWT token for our application
        access_token = create_access_token(
            data={
                "sub": user.get("email", f"fb_{user.get('id')}@facebook.com"),
                "name": user.get("name", ""),
                "picture": user.get("picture", {}).get("data", {}).get("url", ""),
                "provider": "facebook"
            }
        )

        # Redirect to frontend with token
        redirect_url = f"{FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Facebook OAuth2 authentication failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user(request: Request):
    # This endpoint can be used to validate the current user
    # You would typically extract and validate the JWT token here
    return {"message": "OAuth2 authentication is configured"}

@router.get("/logout")
async def logout():
    # In a real app, you might want to invalidate the token
    # For now, just redirect to frontend login page
    return RedirectResponse(url=f"{FRONTEND_URL}/login")