from pydantic import BaseModel 
from typing import Dict

# Define Pydantic Model for Request Body
class AnswerRequest(BaseModel):
    user_id: str
    question_id: str
    selected_option: str
    correct_option: str
    module: str
    explanation: str
    topics: Dict
    question_type: str