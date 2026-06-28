from fastapi import APIRouter, Depends
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse, VerifyOTPRequest, VerifyOTPResponse, GoogleAuthRequest
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import auth_service, google_auth_service

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return {"message": await auth_service.register(db=db, email=req.email, password=req.password) }

@router.post("/login", response_model=LoginResponse)
async def login(req:LoginRequest , db: AsyncSession = Depends(get_db)):
    return {"message": await auth_service.login(db=db, email=req.email, password=req.password) }

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.verify_otp(db=db, email=req.email, otp=req.otp)

@router.post("/google", response_model=VerifyOTPResponse)
async def google_auth(req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    return await google_auth_service.google_login(db=db, code=req.code)