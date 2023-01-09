from datetime import datetime, timedelta
import hashlib
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import User, get_db
from scheme import TokenData


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def create_hash_password(password: str) -> str:
    """
    Hashing password.
    """
    hash_maker = hashlib.new('sha256')
    hash_maker.update(password.encode())
    return hash_maker.hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)) -> User:
    """
    Get and check credentials user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_name(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_user_by_name(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).one()
