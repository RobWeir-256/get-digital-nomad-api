import logging

from sqlmodel import Session, create_engine

logger = logging.getLogger(__name__)

sqlite_file_name = "get-digital-nomad.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=True)
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


# def create_db_and_tables():
#     logging.info("Creating database")
#     SQLModel.metadata.create_all(engine)


# def seed_db():
#     create_countries()
#     create_users()
#     create_visits()
