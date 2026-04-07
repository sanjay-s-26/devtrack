from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the authenticated user for the current request.
    
    Parameters:
        current_user (User): The authenticated user provided by the `get_current_user` dependency.
    
    Returns:
        The `User` instance representing the authenticated user to be serialized as the response.
    """
    return current_user
