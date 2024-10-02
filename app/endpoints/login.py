from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_repository import create_new_user, get_user_by_username
from app.db.database import get_session
from app.schemas.fastapi_schemas import Token
from app.schemas.user_schema import UserAuthentication, UserCreate, UserOut
from app.security.authentication import authenticate_user, create_access_token
from app.security.pwd_crypt import get_hashed_password


loginrouter = APIRouter()


@loginrouter.post('/user', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def post_endpoint(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await get_user_by_username(session, user_data.username)
    if user:
        raise HTTPException(
            detail='Username already taken', status_code=status.HTTP_400_BAD_REQUEST
        )

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_new_user(session, user_data)
    return new_user


@loginrouter.post('/token')
async def login_for_access_token(
    form_data: UserAuthentication,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(user)
    return Token(access_token=access_token, token_type='Bearer')
