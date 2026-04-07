from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using the configured bcrypt CryptContext.
    
    Parameters:
        password (str): Plaintext password to be hashed.
    
    Returns:
        hashed_password (str): Hashed password string suitable for storage.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify that a plaintext password matches a stored password hash.
    
    Parameters:
        plain (str): The candidate plaintext password to verify.
        hashed (str): The stored hashed password to compare against.
    
    Returns:
        bool: `True` if `plain` matches `hashed`, `False` otherwise.
    """
    return pwd_context.verify(plain, hashed)
