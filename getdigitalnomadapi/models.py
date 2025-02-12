from datetime import date, datetime, timezone
import uuid
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

"""
MySQLModel Model
    created_at: updated when record created with UTC time
    updated_at: updated when record last updated with UTC time
"""


class MySQLModel(SQLModel):
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )


"""
User Model
"""


class UserBase(MySQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    full_name: str
    disabled: bool = True
    admin: bool = False


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4, index=True, unique=True
    )  # Move this up to UserBase
    hashed_password: str

    visits: list["Visit"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    full_name: str | None
    disabled: bool = False
    admin: bool = False
    password: str


class UserPublic(UserBase):
    id_uuid: uuid.UUID


class UserPublicWithVisits(UserPublic):
    visits: list["Visit"]


class UserAdmin(UserPublicWithVisits):
    id: int


class UserUpdate(SQLModel):
    username: str | None = None
    hashed_password: str | None = None
    # email: EmailStr | None = None
    full_name: str | None = None
    # disabled: bool | None = None
    # admin: bool | None = None


"""
Token Model
"""


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    # username: str | None = None
    id_uuid: uuid.UUID | None = None


"""
Country Model
https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
"""


class Country(MySQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    official_state_name: str
    code: str = Field(index=True, unique=True)
    schengen: bool = False


"""
Visit Model
"""


class Visit(MySQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    start: date
    end: date | None
    still_visiting: bool = False
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="visits")


"""
Hero and Team Model
"""


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
