import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlmodel import Session, select

from .database import get_session
from .models import TokenData, User
from .security import check_jwt

logger = logging.getLogger(__name__)
SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = check_jwt(token)
        user_id_str: str = payload.get("sub")
        print(user_id_str)
        if user_id_str is None:
            logging.error("payload sub:id is None")
            raise credentials_exception
        token_data = TokenData(id_uuid=user_id_str)
    except ExpiredSignatureError as e:
        logging.error(repr(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=repr(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        logging.error(repr(e))
        raise credentials_exception

    # user = get_user_by_id(id=token_data.id_uuid)
    user = session.exec(select(User).where(User.id == token_data.id_uuid)).first()

    if user is None:
        logging.error("UserId %s is not found", token_data.id_uuid)
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # User must be Admin and Active and in DB
    if not current_user.admin:
        raise HTTPException(status_code=400, detail="User not Admin")
    return current_user
