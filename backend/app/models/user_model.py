from pymongo.collection import Collection
from bson.objectid import ObjectId
from app.utils.db import db
from app.utils.logger import logger

class UserModel:
    def __init__(self):
        self.collection: Collection = db["users"]

    def create_user(self, name: str, email: str) -> dict:
        """Creates a new user with `has_purchased` set to False"""
        if self.collection.find_one({"email": email}):
            logger.info(f"User with email {email} already exists.")
            return {"error": "User already exists"}

        user_data = {
            "name": name,
            "email": email,
            "has_purchased": False
        }
        result = self.collection.insert_one(user_data)
        logger.info(f"Created user with ID: {result.inserted_id}")
        return {"_id": str(result.inserted_id), **user_data}

    def update_has_purchased(self, user_id: str) -> dict:
        """Updates has_purchased to True for the user with given _id"""
        try:
            object_id = ObjectId(user_id)
        except Exception as e:
            logger.error(f"Invalid user ID format: {user_id}")
            return {"error": "Invalid user ID"}

        result = self.collection.update_one(
            {"_id": object_id},
            {"$set": {"has_purchased": True}}
        )

        if result.modified_count == 0:
            logger.warning(f"No user updated for ID: {user_id}")
            return {"error": "User not found or already updated"}

        logger.info(f"Updated has_purchased to True for user ID: {user_id}")
        return {"message": "User updated successfully"}

    def get_user_by_email(self, email: str) -> dict:
        """Fetch user details by email"""
        user = self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
            return user
        return {"error": "User not found"}

    def has_already_purchased(self, email: str) -> dict:
        """Check if the user has already purchased a policy using email"""
        user = self.collection.find_one({"email": email})
        if not user:
            return {"error": "User not found"}
        
        return {
            "email": email,
            "has_purchased": user.get("has_purchased", False)
        }
