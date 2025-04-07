from database.db import users_collection
from models.user import User
import logging

# Initialize the logger
logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)


# Function to create a new user
async def create_user(user_data: User):
    logger.info("Creating new user")
    existing_user = await users_collection.find_one({"name": user_data.name})
    if existing_user:
        logger.info(f"User {user_data.name} already exists")
        return {"message": "User already exists", "user": existing_user}

    user_dict = user_data.model_dumps()
    logger.info("Inserting new user")
    await users_collection.insert_one(user_dict)
    logger.info("User registered successfully")
    return {"message": "User registered successfully", "user": user_dict}


# Function to get user details
async def get_user(name: str):
    logger.info("Getting user data")
    user = await users_collection.find_one({"name": name})
    if user:
        logger.info(f"User {name} found")
        user.pop("_id")  # Remove MongoDB ObjectID
        return user
    logger.info(f"User {name} not found")
    return {"message": "User not found"}


# Function to update user progress
async def update_user_progress(name: str, question: str, module: str, is_correct: bool, points: int):
    logger.info("Updating user progress")
    user = await users_collection.find_one({"name": name})

    if not user:
        logger.info(f"User {name} not found")
        return {"message": "User not found"}
    logger.info("Found user and updating score")
    # Update score
    new_score = user["score"] + points if is_correct else user["score"]
    logger.info("Updated score")
    # Update level based on score
    new_level = determine_level(new_score)
    logger.info("Got new level")

    # Update question history
    new_question_entry = {
        "question": question,
        "module": module,
        "is_correct": is_correct
    }
    logger.info("Updated new question entry")
    await users_collection.update_one(
        {"name": name},
        {"$set": {"score": new_score, "level": new_level},
         "$push": {"question_history": new_question_entry},
         "$inc": {"total_correct": 1} if is_correct else {"total_incorrect": 1}
         }
    )
    logger.info("Updated users progress in users collection")
    return {"message": "User progress updated", "new_score": new_score, "new_level": new_level}


# Function to determine user level
def determine_level(score: int):
    logger.info("Determining level")
    if score >= 200:
        return "Master"
    elif score >= 151:
        return "Expert"
    elif score >= 101:
        return "Advanced"
    elif score >= 51:
        return "Intermediate"
    return "Beginner"
