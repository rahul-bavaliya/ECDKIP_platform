from fastapi import APIRouter

from app.core import get_logger

router = APIRouter()
logger = get_logger()


@router.get("/users")
async def get_users():
    # Meta / X style trace logging with context injection
    logger.info("Fetching application users list", query_limit=100)
    return [
        {"id": 1, "username": "rahul_bavaliya", "role": "admin"},
        {"id": 2, "username": "dev_user", "role": "developer"},
    ]
