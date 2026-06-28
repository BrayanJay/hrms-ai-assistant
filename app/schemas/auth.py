from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str

class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class VerifyOTPResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class GoogleAuthRequest(BaseModel):
      code: str