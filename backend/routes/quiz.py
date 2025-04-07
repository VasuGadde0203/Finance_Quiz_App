from utils.openai_utils import generate_finance_question, generate_learning_material, generate_revision_questions
from fastapi import APIRouter, HTTPException
from database.db import users_collection, questions_collection, revision_questions_collection
from bson import ObjectId
import logging
from fastapi.encoders import jsonable_encoder
from models.models import AnswerRequest

# Initialize the logger
logger = logging.getLogger("quiz_routes")
logger.setLevel(logging.DEBUG)

quiz_router = APIRouter()

LEVELS = {
    "Beginner": 50,
    "Intermediate": 100,
    "Advanced": 150,
    "Expert": 200,
    "Master": 250
}

# @quiz_router.get("/generate_question/")
async def generate_question(user_id: str, level: str, topics: dict):
    """
    Generate a finance quiz question based on the user's level and store it in the database.
    """
    # logger.info("Generating Question...")
    # user = users_collection.find_one({"_id": user_id})
    # # logger.info(f"Got user: {user['username']}")
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    # level = user["level"]  # Get the user’s current level (Beginner, Intermediate, etc.)
    try:
    
        question_data = await generate_finance_question(level, topics)
        logger.info(question_data)

        if not question_data:
            raise HTTPException(status_code=500, detail="Failed to generate question")
        logger.info("Generated question...")
        # Store question in MongoDB
        question_data["user_id"] = str(user_id)
        questions_collection.insert_one(question_data)
        logger.info("Question data inserted into questions collection successfully")
        question_data["_id"] = str(question_data["_id"])
        return question_data
    except Exception as e:
        logger.info(f"Error while generating questions: {e}")
        return None


@quiz_router.post("/start_quiz")
def start_quiz(user_name: str):
    """Initialize a new user in the database."""
    print(users_collection)
    user = users_collection.find_one({"name": user_name})
    logger.info("Got user data while starting quiz")
    if user:
        logger.info("Starting quiz...")
        return {
                "user_id": str(user["_id"]),
                "score": user["score"], 
                "level": user["level"], 
                "questions_attempted": user["questions_attempted"],
                "topics": user["topics"]
                }
    logger.info("Starting new quiz...")
    user_data = {
        "name": user_name,
        "score": 0,
        "level": "Beginner",
        "questions_attempted": [], 
        "topics": {}
    }
    new_user = users_collection.insert_one(user_data)
    logger.info("New user data inserted successfully")
    return {
            "user_id": str(new_user.inserted_id),
            "score": 0,
            "level": "Beginner",
            "questions_attempted": [], 
            "topics": {}
            }


@quiz_router.get("/get_next_question/{user_id}")
async def get_question(user_id: str):
    """Fetch a new question based on the user's level."""
    try: 
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        print("Got user")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        

        question = await generate_question(user_id, user["level"], user["topics"])
        logger.info("Returning question to app")
        logger.info({"status": "success", "question": question, "status_code": 200})
        return {"status": "success", "question": question, "status_code": 200}

    except Exception as e:
        logger.info(f"Error while getting question: {e}")
        return {"status": "failed", "question": None, "status_code": 401}


@quiz_router.post("/submit_answer")
def submit_answer(payload: AnswerRequest):
    user_id = payload.user_id 
    question_id = payload.question_id
    selected_option = payload.selected_option
    correct_option = payload.correct_option
    module = payload.module 
    topics = payload.topics 
    explanation = payload.explanation
    question_type = payload.question_type
    
    """Submit an answer and update user progress."""
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    logger.info("Got users collection")
    
    if question_type == "revision": 
        question = revision_questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info("Stored in revision question collection")
        
    else:
        question = questions_collection.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        logger.info("Stored in question collection")

    is_correct = selected_option == correct_option
    logger.info(f"Selected option: {selected_option}")
    logger.info(f"Correct option: {correct_option}")
    
    points = 10 if is_correct else 0  # Assign points based on correctness
    logger.info(f"Points: {points}")
    # score = user["score"] + points

    # Update user progress in the database
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$push": {
                "questions_attempted": {
                    "question_id": question_id,
                    "module": module,
                    "selected_option": selected_option,
                    "correct": is_correct
                }
            },
            "$inc": {"score": points},
            "$set": {"topics": topics}  # Updating topics in the document
        }
    )

    logger.info("Users collection updated")
    # Check level progression
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    new_level = user["level"]

    for level, required_score in LEVELS.items():
        if user["score"] >= required_score:
            new_level = level
            logger.info("Calculated new level")

    if new_level != user["level"]:
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"level": new_level}})
        logger.info("Updated new level")
    
    # If user has answered 7 questions, switch to learning mode
    if len(user["questions_attempted"]) >= 7:
        return {
        "correct": is_correct,
        "explanation": explanation,
        "new_score": user["score"],
        "new_level": new_level,
        "status_code": 200,
        "learning_mode": True
        }

    return {
        "correct": is_correct,
        "explanation": explanation,
        "new_score": user["score"],
        "new_level": new_level,
        "status_code": 200, 
        "learning_mode": False
    }


@quiz_router.get("/get_learning_material")
def get_learning_material(user_id: str):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        print("Got user")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        score, level, topics = user["score"], user["level"], user["topics"]
        
        learning_material = generate_learning_material(score, level, topics)
        if learning_material:
            print(f"Learning material: {learning_material}")
            return learning_material
        else: 
            return None 
    
    except Exception as e:
        print(f"Error while getting learning material from AI: {e}")
        return None 
    


@quiz_router.get("/get_revision_questions")
def get_revision_questions(user_id: str, learning_material: str):
    try:
        # Fetch user data
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")


        if not learning_material:
            raise HTTPException(status_code=400, detail="Learning material not available")

        # Generate revision questions
        revision_questions = generate_revision_questions(learning_material, num_questions=3)
        if not revision_questions:
            raise HTTPException(status_code=500, detail="Failed to generate revision question")
        
        final_rev_questions = []
        
        for rq in revision_questions["questions"]:
            rq["user_id"] = str(user_id)
            revision_questions_collection.insert_one(rq)
            rq['_id'] = str(rq["_id"])
            final_rev_questions.append(rq)
        
        

        return {"questions": final_rev_questions}

    except Exception as e:
        print(f"Error generating revision questions: {e}")
        raise HTTPException(status_code=500, detail="Error generating revision questions")
