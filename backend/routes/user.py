from fastapi import APIRouter
from models.user import User
from services.service import create_user, get_user, update_user_progress
import logging

# Initialize the logger
logger = logging.getLogger("user_routes")
logger.setLevel(logging.DEBUG)

router = APIRouter()

# Register a new user
@router.post("/register")
async def register_user(user: User):
    logger.info("Registering user")
    return await create_user(user)

# Get user details
@router.get("/user/{name}")
async def fetch_user(name: str):
    logger.info("Fetching user")
    return await get_user(name)

# Update user progress after a quiz question
@router.post("/update_progress")
async def update_progress(name: str, question: str, module: str, is_correct: bool, points: int):
    logger.info("Updating progress")
    return await update_user_progress(name, question, module, is_correct, points)
