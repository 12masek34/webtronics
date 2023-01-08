import os
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from database import User, get_db
from scheme import UserCreate, UserInDB, UserSchema
from services import create_access_token, create_hash_password, get_current_user


app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


@app.post('/create', description='Register the User')
async def user_create(user: UserCreate,  db: Session = Depends(get_db)) -> UserCreate:
    """
    Registration user.
    """
    hash_password = create_hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hash_password)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail='user name already exists')
    return user


@app.post('/token')
async def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Get token.
    """
    try:
        user = db.query(User).filter(User.username == data.username).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail='user not found')
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    hashed_password = create_hash_password(data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/users/me/', response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Check me.
    """
    return UserInDB(
        username=current_user.username,
        hashed_password=current_user.hashed_password,
    )
