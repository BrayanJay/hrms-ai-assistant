from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.otp import OTP
from fastapi import HTTPException, status
from app.core.security import hash_password, generate_otp, hash_otp, verify_password, create_access_token, create_refresh_token, verify_hashed_otp
from datetime import datetime, timezone
from app.services.email_service import send_otp_email

async def register(db: AsyncSession, email: str, password: str) -> str:

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email has been already registered"
        )
        
    new_user = User(email=email, hashed_password=hash_password(password))
    db.add(new_user)
    await db.flush()

    create_otp =  generate_otp()
    hashed_otp = hash_otp(create_otp)

    new_otp = OTP(user_id=new_user.id, hashed_otp=hashed_otp)
    db.add(new_otp)
    await db.commit()

    await send_otp_email(email=email, otp=create_otp)

    return "User created successfully and Send the OTP for verification"

async def login(db: AsyncSession,email: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worng username or password")
    if not existing_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is either inactived or suspended. Please contact help desk support team.")
    
    user_id = str(existing_user.id)
    user_role = existing_user.role
    

    return { "access_token": create_access_token(user_id,user_role), "refresh_token": create_refresh_token(user_id), "token_type": "bearer" }

async def verify_otp(db: AsyncSession, email: str, otp: str) -> dict:
    user_result = await db.execute(select(User).where(User.email == email))
    existing_user = user_result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User")
    
    otp_result = await db.execute(select(OTP).where(OTP.user_id == existing_user.id, OTP.is_used == False, OTP.expires_at > datetime.now(timezone.utc)).order_by(OTP.created_at.desc()).limit(1))
    latest_otp = otp_result.scalar_one_or_none()

    if not latest_otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid OTP found")

    if not verify_hashed_otp(otp, latest_otp.hashed_otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP Not verified")
    
    latest_otp.is_used = True
    existing_user.is_verified = True

    user_id = str(existing_user.id)
    user_role = existing_user.role

    await db.commit()

    acc_tkn = create_access_token(user_id, user_role)
    ref_tkn = create_refresh_token(user_id)

    return {"access_token": acc_tkn, "refresh_token": ref_tkn, "token_type": "bearer"}