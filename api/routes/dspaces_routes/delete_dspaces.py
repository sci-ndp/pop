from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict
from api.services import dspaces_services
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.delete("/dspaces")
async def delete_current_user_dspaces(current_user: Dict = Depends(get_current_user)):
    """
    Delete the dspaces instance for the currently authenticated user.
    """
    try:
        user_id = current_user["id"]
    except KeyError:
        raise HTTPException(status_code=400, detail="User ID not found in the current user information")

    try:
        result = dspaces_services.delete_dspaces_resources(user_id)
        return {"message": f"dspaces instance deleted for user {user_id}", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/dspaces/{user_id}",
               description="""
               Delete the dspaces instance for a specific user ID.
               Requires the current user to be authenticated (e.g., for admin purposes).
               """)
async def delete_specific_user_dspaces(user_id: str, current_user: Dict = Depends(get_current_user)):
    try:
        # if "admin" not in current_user.get("roles", []):
        #     raise HTTPException(status_code=403, detail="Not authorized to delete other users' dspaces")
        
        result = dspaces_services.delete_dspaces_resources(user_id)
        return {"message": f"dspaces instance deleted for user {user_id}", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")