import uuid
from datetime import date, datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

"""
Token Model
"""


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id_uuid: uuid.UUID | None = None


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
    email_validated: bool = (
        False  # TODO - send email for confirmation before enabling user access
    )


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
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
    id: uuid.UUID


class UserPublicWithVisits(UserPublic):
    visits: list["VisitPublicWithCountry"]


class UserAdmin(UserPublicWithVisits):
    pass


class UserUpdate(SQLModel):
    username: str | None = None
    hashed_password: str | None = None
    # email: EmailStr | None = None
    full_name: str | None = None
    # disabled: bool | None = None
    # admin: bool | None = None


"""
Country Model
https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv
"""


class CountryBase(MySQLModel):
    name: str = Field(index=True, unique=True)
    # official_state_name: str
    code: str = Field(index=True, unique=True)
    schengen: bool = False


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    visits: list["Visit"] = Relationship(back_populates="country")


class CountryCreate(CountryBase):
    pass


class CountryPublic(CountryBase):
    id: int


class CountryUpdate(SQLModel):
    name: str | None = None
    official_state_name: str | None = None
    code: str | None = None
    schengen: bool | None = None


"""
Visit Model
"""


class VisitBase(MySQLModel):
    start: date
    end: date | None
    # still_visiting: bool = False


class Visit(VisitBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user: User | None = Relationship(back_populates="visits")
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    country: Country | None = Relationship(back_populates="visits")
    country_id: int | None = Field(default=None, foreign_key="country.id")


class VisitCreate(VisitBase):
    pass


class VisitPublic(VisitBase):
    id: int
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    country_id: int | None = Field(default=None, foreign_key="country.id")


class VisitUpdate(SQLModel):
    start: date | None = None
    end: date | None = None
    still_visiting: bool | None = None


class VisitPublicWithCountry(VisitPublic):
    country: CountryPublic


class VisitPublicWithCountryAndUser(VisitPublic):
    country: CountryPublic
    user: UserPublic


class VisitUserMePublic(SQLModel):
    id: int
    country_id: int
    start: date | None
    end: date | None


class VisitsUserMePublicSummary(SQLModel):
    num_visit: int
    visits: list[VisitUserMePublic]
