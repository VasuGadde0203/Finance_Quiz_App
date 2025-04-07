from pydantic import BaseModel
from typing import List, Dict

# User Schema
class User(BaseModel):
    user_id: str
    name: str
    score: int = 0  # Initial score
    level: str = "Beginner"
    total_correct: int = 0  # Total correct answers
    total_incorrect: int = 0  # Total incorrect answers
    question_history: List[Dict] = []  # Stores past questions
