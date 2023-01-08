from pydantic import BaseModel, constr


class UserCreate(BaseModel):
    """
    Create user schema.
    """
    username: str
    password: constr(min_length=7, max_length=100)
