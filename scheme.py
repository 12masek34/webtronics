from pydantic import BaseModel, constr


class UserCreate(BaseModel):
    """
    Create user schema.
    """
    username: str
    password: constr(min_length=7, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSchema(BaseModel):
    username: str


class UserInDB(UserSchema):
    hashed_password: str

    class Config:
        orm_mode = True


class PostSchema(BaseModel):
    id: int
    author_id: int
    text: str

    class Config:
        orm_mode = True


class DeletePostSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True
