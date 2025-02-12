from datetime import timedelta
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..database import get_session
from ..security import create_access_token, verify_password
from ..models import Token, User

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours

router = APIRouter(
    prefix="/token",
    tags=["token"],
)


@router.post("/")
async def login_for_access_token(
    *,
    session: Session = Depends(get_session),
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    email = form_data.username
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id_uuid)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
