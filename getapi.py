from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List

app = FastAPI()

# MongoDB connection settings
mongo_details = "mongodb://localhost:27017"
client = AsyncIOMotorClient(mongo_details)
database = client.test  # Replace with your database name
user_collection = database.get_collection("users")  # Replace with your collection name

# Pydantic model for user response
class UserResponse(BaseModel):
    id: str
    name: str
    email: str

# Helper function to convert ObjectId to str
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }

# Function to retrieve all users from the database
async def get_all_users_from_db():
    users = await user_collection.find().to_list(length=None)  # Fetch all users
    return [user_helper(user) for user in users]

# GET endpoint to retrieve all users
@app.get("/crud", response_model=List[UserResponse],responses={
    200: {
        "description": "List of all users",
        "content": {
            "application/json": {
                "example": [
                    {"id": "64d8ec9df1c67c43a9e1b2b1", "name": "John Doe", "email": "john.doe@example.com"},
                
                ]
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {"detail": "An unexpected error occurred"}
            }
        }
    }
})
         
         
async def get_all_users():
    users = await get_all_users_from_db()
    return users

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
