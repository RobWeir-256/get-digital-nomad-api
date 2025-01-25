from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from database import create_db_and_tables, get_user, seed
from models import User, UserPublic, Token, TokenData

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PRE_FIX_URL = "/api/v1"

# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#         "id": 1,
#     }
# }
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=PRE_FIX_URL + "/token")
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return User(**user_dict)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post(PRE_FIX_URL + "/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get(PRE_FIX_URL + "/users/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get(PRE_FIX_URL + "/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


# from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# class HeroTeamLink(SQLModel, table=True):
#     team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
#     hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
#     is_training: bool = False

#     team: "Team" = Relationship(back_populates="hero_links")
#     hero: "Hero" = Relationship(back_populates="team_links")


# class Team(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     headquarters: str

#     hero_links: list[HeroTeamLink] = Relationship(back_populates="team")


# class Hero(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     secret_name: str
#     age: int | None = Field(default=None, index=True)

#     team_links: list[HeroTeamLink] = Relationship(back_populates="hero")


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine = create_engine(sqlite_url, echo=True)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# def create_heroes():
#     with Session(engine) as session:
#         team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
#         team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

#         hero_deadpond = Hero(
#             name="Deadpond",
#             secret_name="Dive Wilson",
#         )
#         hero_rusty_man = Hero(
#             name="Rusty-Man",
#             secret_name="Tommy Sharp",
#             age=48,
#         )
#         hero_spider_boy = Hero(
#             name="Spider-Boy",
#             secret_name="Pedro Parqueador",
#         )
#         deadpond_team_z_link = HeroTeamLink(team=team_z_force, hero=hero_deadpond)
#         deadpond_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_deadpond, is_training=True
#         )
#         spider_boy_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_spider_boy, is_training=True
#         )
#         rusty_man_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_rusty_man
#         )

#         session.add(deadpond_team_z_link)
#         session.add(deadpond_preventers_link)
#         session.add(spider_boy_preventers_link)
#         session.add(rusty_man_preventers_link)
#         session.commit()

#         for link in team_z_force.hero_links:
#             print("Z-Force hero:", link.hero, "is training:", link.is_training)

#         for link in team_preventers.hero_links:
#             print("Preventers hero:", link.hero, "is training:", link.is_training)


# def update_heroes():
#     with Session(engine) as session:
#         hero_spider_boy = session.exec(
#             select(Hero).where(Hero.name == "Spider-Boy")
#         ).one()
#         team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

#         spider_boy_z_force_link = HeroTeamLink(
#             team=team_z_force, hero=hero_spider_boy, is_training=True
#         )
#         team_z_force.hero_links.append(spider_boy_z_force_link)
#         session.add(team_z_force)
#         session.commit()

#         print("Updated Spider-Boy's Teams:", hero_spider_boy.team_links)
#         print("Z-Force heroes:", team_z_force.hero_links)

#         for link in hero_spider_boy.team_links:
#             if link.team.name == "Preventers":
#                 link.is_training = False

#         session.add(hero_spider_boy)
#         session.commit()

#         for link in hero_spider_boy.team_links:
#             print("Spider-Boy team:", link.team, "is training:", link.is_training)


# def main():
#     create_db_and_tables()
#     create_heroes()
#     update_heroes()


# if __name__ == "__main__":
#     main()
