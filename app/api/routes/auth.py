from fastapi import APIRouter, Depends, Response, Request
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, VerifyOTPRequest, GoogleAuthRequest
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import auth_service, google_auth_service
from app.api.dependencies import require_admin
from app.core.limiter import limiter

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