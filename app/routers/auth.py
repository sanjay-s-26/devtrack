from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserResponse
from app.utils.hashing import hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account and persist it to the database.
    
    Parameters:
        user_data (UserCreate): Registration data containing email, username, and plaintext password.
    
    Returns:
        User: The newly created user with persisted fields (e.g., id) populated.
    
    Raises:
        HTTPException: 400 if the email is already registered or the username is already taken.
    """
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(user_data.password)
    user = User(email=user_data.email, username=user_data.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, status_code=200)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and issue a JWT access token.
    
    Parameters:
        data (LoginRequest): Credentials with `email` and `password` used to authenticate the user.
    
    Returns:
        Token: Object containing `access_token` (JWT for the authenticated user) and `token_type` set to `"bearer"`.
    
    Raises:
        HTTPException: With status code 401 when the email does not exist or the password is incorrect.
    """
    user = db.query(User).filter(User.email == data.email).first()

    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")
