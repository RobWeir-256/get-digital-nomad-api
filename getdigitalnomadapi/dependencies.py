import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import Session

from .database import get_session, get_user_by_id, get_user_by_username
from .security import check_jwt
from .models import TokenData, User


logger = logging.getLogger(__name__)
SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # try:
    #     payload = check_jwt(token)
    #     username: str = payload.get("sub")
    #     if username is None:
    #         raise credentials_exception
    #     token_data = TokenData(username=username)
    # except InvalidTokenError:
    #     raise credentials_exception
    # user = get_user_by_username(username=token_data.username)
    # if user is None:
    #     raise credentials_exception
    # return user
    try:
        payload = check_jwt(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(id=user_id_str)
    except InvalidTokenError:
        raise credentials_exception
    # user = get_user_by_username(username=token_data.username)
    user = get_user_by_id(id=token_data.id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
