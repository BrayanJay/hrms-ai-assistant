from fastapi import HTTPException, Request

import base64, json

def require_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        padded = token.split(".")[1]
        padded += "=" * (-len(padded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        data = payload["data"]
        return {"sub": data["useruuid"], "username": data["username"]}
    except Exception:
          raise HTTPException(status_code=401, detail="Invalid token")

#In case if there will be a seperate require_admin() comes in future, for now all users have access to admin
require_admin = require_user