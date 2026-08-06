from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, VerifyOTPRequest, GoogleAuthRequest
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import auth_service, google_auth_service
from app.api.dependencies import require_admin
from app.core.limiter import limiter
from app.models.user import User
from sqlalchemy import select
from app.core.security import create_access_token, decode_token

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
@limiter.limit("5/minute")
async def register(request: Request, req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return {"message": await auth_service.register(db=db, email=req.email, password=req.password) }

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, req:LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await auth_service.login(db=db, email=req.email, password=req.password)

    response.set_cookie(key="access_token", value=result["access_token"], httponly=True, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=result["refresh_token"], httponly=True, samesite="lax", secure=False)

    return {"message": "Login successfull"}

@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    payload = decode_token(token)                          # raises 401 if expired/invalid
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    # fetch user from DB to get their role
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    response.set_cookie(key="access_token", value=create_access_token(str(user.id), user.role), httponly=True, samesite="lax", secure=False)
    return {"message": "Token refreshed"}

@router.post("/verify-otp")
@limiter.limit("5/minute")
async def verify_otp(request: Request, req: VerifyOTPRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result =  await auth_service.verify_otp(db=db, email=req.email, otp=req.otp)

    response.set_cookie(key="access_token", value=result["access_token"], httponly=True, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=result["refresh_token"], httponly=True, samesite="lax", secure=False)

    return {"message": "Login successful"}

@router.post("/google")
async def google_auth(req: GoogleAuthRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await google_auth_service.google_login(db=db, code=req.code)

    response.set_cookie(key="access_token", value=result["access_token"], httponly=True, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=result["refresh_token"], httponly=True, samesite="lax", secure=False)

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")

    return {"message": "User logout successful"}

@router.get("/me")
async def me( current_user: dict = Depends(require_admin)):
    return current_user