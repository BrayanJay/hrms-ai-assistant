from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException, status
from app.core.security import decode_token

security = HTTPBearer()

def require_admin(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    decoded_token = decode_token(token=token)
    
    if not decoded_token["role"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action required admin access"
        )
    return decoded_token["sub"]