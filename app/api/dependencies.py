from fastapi import HTTPException, Request
from app.core.logging import get_logger

import base64, json

logger = get_logger(__name__)

def require_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        logger.warning("auth failed — missing bearer token", extra={"path": request.url.path})
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        padded = token.split(".")[1]
        padded += "=" * (-len(padded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        data = payload["data"]
        return {"sub": data["useruuid"], "username": data["username"]}
    except Exception:
        logger.warning("auth failed — invalid token", extra={"path": request.url.path})
        raise HTTPException(status_code=401, detail="Invalid token")

#In case if there will be a seperate require_admin() comes in future, for now all users have access to admin
require_admin = require_user