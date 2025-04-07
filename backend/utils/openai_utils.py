import openai
import os
from dotenv import load_dotenv
import json
import logging
import asyncio 
from openai import AzureOpenAI

# Initialize the logger
logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)


load_dotenv()  # Load API key from .env

AZURE_OPENAI_API_KEY = "7219267fcc1345cabcd25ac868c686c1"
AZURE_OPENAI_ENDPOINT = "https://stock-agent.openai.azure.com/"

# Create an Azure OpenAI Client
azure_client = AzureOpenAI(azure_endpoint=AZURE_OPENAI_ENDPOINT,
                           api_key=AZURE_OPENAI_API_KEY,
                           api_version="2024-05-01-preview")

async def generate_finance_question(level: str, topics: dict):
    """
    Generates a finance-related question based on the user's level.
    """
    logger.info("Generating finance question...")
    prompt = f"""
        Generate a finance-related multiple-choice question (MCQ) for a user at {level} level.

        🟢 The question should be based on the user's past performance (If topics are empty then it may be it is a first question):
        - Below are the topics user gave answers, there may be some correct answer and some wrong answers for some topics, so based
          on that, classify any topic as weak or strong topic: 
          {topics}

        📌 Guidelines:
        - Cover finance topics like investing, budgeting, taxes, insurance, or economics.
        - Provide four answer choices, clearly marking the correct one.
        - Include a short explanation for the correct answer.
        - Avoid repeating the same topic consecutively.

        📌 JSON Response Format:
        {{
            "question": "Your finance question?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_option_index": 1
            "explanation": "Brief explanation of the correct answer.",
            "module": "Module of the question"
        }}
    """

    logging.info("Sending question to openai...")
    response = azure_client.chat.completions.create(
        model="model-4o",
        messages=[{"role": "system", "content": "You are a financial education assistant."},
                  {"role": "user", "content": prompt}]
    )
    logger.info("Response received from openai...")
    try:
        # Load JSON data asynchronously
        data = await asyncio.to_thread(json.loads, response.choices[0].message.content)
        
        logger.info("Returning response")
        
        return {
        "question_text": data["question"],
        "options": data["options"],
        "correct_option_index": data["correct_option_index"],
        "explanation": data["explanation"],
        "module": data["module"]
    }
    except Exception as e:
        logger.error("Error generating question:", e)
        return None

def generate_learning_material(score: int, level: str, topics: dict):
    logger.info("Generating learning material")
    incorrect_topics = {k: v["incorrect_answers"] for k, v in topics.items() if v["incorrect_answers"] > 0}
    
    if not incorrect_topics:
        return {"message": "No incorrect answers. Well done!"}
    logger.info("Got incorrect answers")
    
    prompt_text = f"""
    You are an expert finance tutor helping learners improve their financial knowledge through a game-like experience.
    The user has completed a quiz and here is their performance:

    - Score: {score}
    - Level: {level}
    - Topics Performance: {incorrect_topics}

    Based on the incorrect answers, generate a **concise, engaging, and easy-to-understand** learning module (10-15 lines) for the topics where the user made mistakes.
    Use **real-life examples** and **simple explanations** to make it engaging. Keep it conversational and interactive.
    Avoid unnecessary details—focus on key takeaways the user must learn.

    Example format:
    👉 **Topic:** Budgeting  
    📌 **Key Insight:** Budgeting helps track income and expenses, ensuring you don’t overspend.  
    💡 **Example:** Imagine earning $1000/month. If you allocate $300 for rent, $200 for food, and $100 for savings, you have $400 left. Without a budget, you might overspend and save nothing!  
    🔎 **Quick Tip:** Use the 50/30/20 rule—50% needs, 30% wants, 20% savings.

    Generate similar modules for the incorrect topics.
    """
    logger.info("Requesting openAI")
    response = azure_client.chat.completions.create(
        model="model-4o",  # Use "gpt-3.5-turbo" for a cheaper option
        messages=[{"role": "system", "content": "You are a financial education assistant"},
                {"role": "user", "content": prompt_text}],
        max_tokens=500
    )
    
    try:
        logger.info("Extracting response")
        learning_material = response.choices[0].message.content
        if learning_material:
            logger.info("Got Learning material")
            return {"learning_material": learning_material}
        return None
    
    except Exception as e:
        print(f"Error generating learning material: {e}")
        return None
        
def generate_revision_questions(learning_material, num_questions=3):
    """Generate revision questions using OpenAI API"""
    prompt = f"""Based on the following learning material, generate {num_questions} multiple-choice revision questions. 
    Each question should have four options and indicate the correct option index (0-based). 
    Format the response in JSON as follows: 
    {{"questions": [{{"question_text": "...", "options": ["A", "B", "C", "D"], "correct_option_index": 1, "explanation":"...", "module": "..."}}]}}.

    Learning Material:
    {learning_material}

    Questions:
    """
    response = azure_client.chat.completions.create(
        model="model-4o",
        messages=[
            {"role": "system", "content": "You are a finance expert generating quiz questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    # Convert OpenAI response to JSON format
    try:
        questions = eval(response.choices[0].message.content)  # Ensure safe parsing
        print(f"Revision questions: {questions}")
        return questions
    except Exception as e:
        print(f"Error parsing OpenAI response: {e}")
        return {"questions": []}