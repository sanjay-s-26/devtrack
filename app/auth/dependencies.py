from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate an access token and return the corresponding active User.
    
    Decodes the provided bearer token to obtain a subject user ID, looks up that user in the database, and enforces that the token is valid and the user is present and active.
    
    Returns:
        User: The active User instance identified by the token's `sub` claim.
    
    Raises:
        HTTPException: 401 with detail "Invalid or expired token" if the token cannot be decoded.
        HTTPException: 401 with detail "User not found or inactive" if no matching active user exists.
    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(payload.get("sub"))

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user
