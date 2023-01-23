import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from database import Post, PostLike, User, get_db
from scheme import (
    DeletePostSchema,
    PostLikeSchema,
    PostSchema,
    UserCreate,
    UserInDB,
    UserPostLikeSchema,
)
from services import (
    create_access_token,
    create_hash_password,
    get_current_user,
)


app = FastAPI()
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


@app.post('/create')
async def user_create(user: UserCreate,
                      db: Session = Depends(get_db)) -> UserCreate:
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
async def login(data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    """
    Get token.
    """
    try:
        user = db.query(User).filter(User.username == data.username).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail='user not found')
    hashed_password = create_hash_password(data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserInDB:
    """
    Check me.
    """
    return current_user


@app.post('/create-post')
async def create_post(
        text: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> PostSchema:
    """
    Create post by auth user.
    """
    post = Post(author_id=current_user.id, text=text)
    db.add(post)
    db.commit()
    return post


@app.get('/list-posts')
async def list_all_posts(db: Session = Depends(get_db)) -> list[PostSchema]:
    """
    List all posts.
    """
    return db.query(Post).all()


@app.delete('/delete-post')
async def delete_post_by_id(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> DeletePostSchema:
    """
    Delete your post.
    """
    try:
        post = db.query(Post).filter(Post.id == post_id,
                                     Post.author_id == current_user.id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail='post not found')
    db.delete(post)
    db.commit()
    return post


@app.patch('/patch-post')
async def patch_post_by_id(
        post_id: int,
        patch_text: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> PostSchema:
    """
    Patch your post.
    """
    try:
        post = db.query(Post).filter(Post.id == post_id,
                                     Post.author_id == current_user.id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail='post not found')
    post.text = patch_text
    db.add(post)
    db.commit()
    return post


@app.post('/like-post')
async def like_post_by_id(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
) -> PostLikeSchema:
    """
    Like some post.
    """
    try:
        post = db.query(Post).filter(Post.id == post_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail='post not found')
    if post.author_id == current_user.id:
        raise HTTPException(status_code=400, detail='you cannot like your post')
    post_like = PostLike(user_id=current_user.id, post_id=post.id)
    db.add(post_like)
    db.commit()
    return post_like


@app.get('/check-likes/{post_id}')
async def check_likes_post_by_id(
        post_id: int,
        db: Session = Depends(get_db)) -> list[UserPostLikeSchema]:
    """
    Check, who like this post.
    """
    user_ids = db.scalars(
        db.query(PostLike.user_id).filter(PostLike.post_id == post_id)).all()
    if not user_ids:
        raise HTTPException(
            status_code=404, detail=f'liks by post id == {post_id} not found.')
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return users

# test