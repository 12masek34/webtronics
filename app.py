from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from scheme import UserCreate


app = FastAPI()



@app.post('/create', description='Register the User')
async def user_create(user: UserCreate) -> UserCreate:
    return user
