from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional

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

# Pydantic model for user update request
class UserUpdate(BaseModel):
    id: str  # MongoDB document ID
    name: Optional[str] = None
    email: Optional[str] = None

# Pydantic model for new user creation
class UserCreate(BaseModel):
    name: str
    email: str

# Helper function to convert ObjectId to str
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }

# Function to insert a new user into the database
async def add_user_to_db(user_data: UserCreate):
    user = {
        "name": user_data.name,
        "email": user_data.email
    }
    
    result = await user_collection.insert_one(user)
    new_user = await user_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)



# POST endpoint to create a new user
@app.post("/crud", response_model=UserResponse,responses={
    201: {
        "description": "User created successfully",
        "content": {
            "application/json": {
                "example": {"id": "64d8ec9df1c67c43a9e1b2b3", "name": "New User", "email": "new.user@example.com"}
            }
        }
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid input data"}
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
async def create_user(user_create: UserCreate):
    new_user = await add_user_to_db(user_create)
    return new_user



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
