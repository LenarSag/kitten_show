from datetime import datetime, timedelta
from typing import Annotated, Optional
import uuid


from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.crud.user_repository import get_user_by_id, get_user_by_username
from app.db.database import get_session
from app.schemas.fastapi_schemas import TokenData
from app.security.pwd_crypt import verify_password
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, API_URL, SECRET_KEY


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{API_URL}/auth/token/')


async def authenticate_user(
    session: Annotated[AsyncSession, Depends(get_session)], username: str, password: str
) -> Optional[User]:
    user = await get_user_by_username(session, username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User) -> str:
    to_encode = {'sub': str(user.id)}
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = uuid.UUID(payload.get('sub'))
        if user_id is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION
    user = await get_user_by_id(session, token_data.user_id)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user
