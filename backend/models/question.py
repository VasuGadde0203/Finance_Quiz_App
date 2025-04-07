from pydantic import BaseModel

class Question(BaseModel):
    question_id: str
    module: str
    question_text: str
    options: list
    correct_option: int
    explanation: str
