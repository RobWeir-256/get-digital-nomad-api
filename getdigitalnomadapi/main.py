import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI

from .database import create_db_and_tables, seed_db
from .internal import admin
from .routers import countries, token, users, visits, me

PREFIX_API_V1 = "/api/v1"


def adj_tz(*ags):
    return datetime.now(timezone.utc).timetuple()


logging.Formatter.converter = adj_tz
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ | %(levelname)-8s | %(name)s->%(filename)s:%(lineno)-3s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
logger.info("Starting App")
# External libraries can be noisy so set them differently than the global logging level
logging.getLogger("passlib").setLevel(logging.INFO)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.CRITICAL)
logging.getLogger("python_multipart").setLevel(logging.INFO)
logging.getLogger("python_multipart").setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_db()
    yield
    logger.info("Exiting App")


app = FastAPI(lifespan=lifespan)

api_v1_router = APIRouter(prefix=PREFIX_API_V1)
api_v1_router.include_router(token.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(me.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(countries.router)
api_v1_router.include_router(visits.router)
app.include_router(api_v1_router)
