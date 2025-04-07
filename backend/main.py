from fastapi import FastAPI
from routes.user import router
from routes.quiz import quiz_router
import logging

# Initialize the logger
logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)

app = FastAPI()

# Include API Routes
app.include_router(router)
app.include_router(quiz_router, prefix="/quiz")

@app.get("/")
def home():
    logging.info("Welcome to quiz app")
    return {"message": "Welcome to the Finance Quiz API"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
