from datetime import datetime, timezone
import uuid
from sqlmodel import Field, Relationship, SQLModel
from typing import List

"""
*** User Model
"""


class UserBase(SQLModel):
    username: str
    email: str = Field(index=True, unique=True)
    full_name: str
    disabled: bool
    created_at: datetime
    updated_at: datetime
    # created_at: datetime | None = Field(
    #     default_factory={lambda: datetime.now(timezone.utc)}
    # )
    # updated_at: datetime | None = Field(
    #     default_factory={lambda: datetime.now(timezone.utc)},
    #     sa_column_kwargs={"onupdate": {lambda: datetime.now(timezone.utc)}},
    # )


class User(UserBase, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


class UserPublic(UserBase):
    id: uuid.UUID


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    username: str | None = None
    hashed_password: str | None = None
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


"""
*** Token Model
"""


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


"""
*** Hero and Team Model
"""


class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    is_training: bool = False

    team: "Team" = Relationship(back_populates="hero_links")
    hero: "Hero" = Relationship(back_populates="team_links")


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    hero_links: list[HeroTeamLink] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_links: list[HeroTeamLink] = Relationship(back_populates="hero")
