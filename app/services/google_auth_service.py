from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from jose import jwt
from app.core.config import settings

async def google_login(db: AsyncSession, code: str) -> dict:

    # Step 1 — exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
              data={
                  "code": code,
                  "client_id": settings.google_client_id,
                  "client_secret": settings.google_client_secret,
                  "redirect_uri": settings.google_redirect_uri,
                  "grant_type": "authorization_code",
              }
        )

    token_data = response.json()
    id_token = token_data.get("id_token")

    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate with Google"
        )
    
    # Step 2 — fetch public keys and verify id_token
    async with httpx.AsyncClient() as client:
        jwks_response = await client.get("https://www.googleapis.com/oauth2/v3/certs")
    
    jwks = jwks_response.json()

    try:
        payload = jwt.decode(id_token, jwks, algorithms=["RS256"], audience=settings.google_client_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
    
    # Step 3 — extract user info from payload
    google_id = payload.get("sub")
    email = payload.get("email")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token claims"
        )

    # Step 4 — find or create user in DB
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.google_id = google_id
        else:
            user = User(email=email, google_id=google_id, is_verified=True)
            db.add(user)

    await db.flush()

    user_id = str(user.id)
    user_role = user.role
    await db.commit()

    # Step 5 — issue your own tokens
    return {"access_token": create_access_token(user_id, user_role), "refresh_token": create_refresh_token(user_id), "token_type": "bearer"}
