from datetime import timedelta
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..routers.users import auth_user_by_email, auth_user_by_username
from ..security import create_access_token
from ..models import Token

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 5

router = APIRouter(
    prefix="/token",
    tags=["token"],
)


@router.post("/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # user = auth_user_by_username(name=form_data.username, password=form_data.password)
    user = auth_user_by_email(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
