from fastapi import HTTPException, status, Request
from app.core.security import decode_token

def require_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    decoded_token = decode_token(token=token)
    
    if decoded_token["role"] != "admin":
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return decoded_token

def require_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    decoded_token = decode_token(token=token)