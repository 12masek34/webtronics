from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import User, get_db
from scheme import UserCreate
from services import create_hash_password


app = FastAPI()



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
