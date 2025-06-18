from fastapi import Depends, HTTPException
from app.api.deps.auth import get_current_user
from app.models.user import User

def require_admin(current_user: User = Depends(get_current_user)):
    if "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user
