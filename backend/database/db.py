from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/vasu"  # Change this if using a cloud DB
client = MongoClient(MONGO_URI)
db = client["finance_education"]  # Database name

users_collection = db["users"]  # Collection for storing user data
questions_collection = db["questions"]
revision_questions_collection = db["revision_questions"]