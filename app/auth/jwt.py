from datetime import datetime, timedelta

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.config import settings


def create_access_token(data: dict) -> str:
    """
    Create a JSON Web Token (JWT) by encoding the provided claims and adding an expiration.
    
    Parameters:
        data (dict): Claims to include in the token payload (will be copied; do not expect the original to be modified).
    
    Returns:
        str: Encoded JWT string with an `exp` (expiration) claim set to now plus the configured access token lifetime.
    """
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decode a JWT access token and return its payload if the token is valid.
    
    Parameters:
        token (str): JWT access token string to decode.
    
    Returns:
        dict: Decoded token claims when the token is valid.
        None: If the token is invalid or has expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (JWTError, ExpiredSignatureError):
        return None
