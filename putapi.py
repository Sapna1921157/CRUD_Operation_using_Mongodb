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

# Helper function to convert ObjectId to str
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }

# Function to update a user in the database
async def update_user_in_db(user_id: str, update_data: UserUpdate):
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    result = await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User updated successfully"}

# PUT endpoint to update a user, with ID provided in the request body
@app.put("/crud", response_model=UserResponse, responses={
    200: {
        "description": "User updated successfully",
        "content": {
            "application/json": {
                "example": {"id": "64d8ec9df1c67c43a9e1b2b1", "name": "Updated Name", "email": "updated.email@example.com"}
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
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {"detail": "User not found"}
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
async def update_user(user_update: UserUpdate):
    user_id = user_update.id
    result = await update_user_in_db(user_id, user_update)
    updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
    return user_helper(updated_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
