from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict

from api.services import dspaces_services
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()


@router.post("/dspaces")
async def create_dspaces(current_user: Dict = Depends(get_current_user)):
    """
    Create a new dspaces instance for a user in a unique namespace.
    """
    try:
        user_id = current_user["id"]
    except KeyError:
        raise HTTPException(status_code=400, detail="User ID not found in the current user information")

    try:
        result = dspaces_services.create_dspaces_resources(user_id)
        return {"message": f"dspaces instance created for user {user_id}", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")