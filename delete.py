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

# Pydantic model for user deletion request
class UserDelete(BaseModel):
    id: str  # MongoDB document ID

# Helper function to convert ObjectId to str
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }



# Function to delete a user from the database
async def delete_user_from_db(user_id: str):
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}




# DELETE endpoint to remove a user
@app.delete("/crud", response_model=dict, responses={
    204: {
        "description": "User deleted successfully"
    },
    404: {
        "description": "User not found",
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
async def delete_user(user_delete: UserDelete):
    user_id = user_delete.id
    result = await delete_user_from_db(user_id)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
