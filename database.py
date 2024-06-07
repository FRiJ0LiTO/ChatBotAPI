from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
import os
from models import User, Question, FrequentlyAskedQuestion, EditQuestion
from own_gpt import model_response
from dotenv import load_dotenv
from passlib.context import CryptContext
from pymongo.errors import PyMongoError
from pymongo import ASCENDING
from datetime import datetime

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

client_url = os.getenv('ATLAS_URI')
database_name = os.getenv('DB_NAME')

client = AsyncIOMotorClient(client_url)
database = client[database_name]
questions_collection = database["questions"]
users_collection = database["neoris"]
faq_collection = database["faq"]


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_user(user: User):
    try:
        user.password = get_password_hash(user.password)
        await users_collection.insert_one(jsonable_encoder(user))
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def switch_disable_user(user_id: str, enable: bool):
    try:
        query = {"_id": user_id}
        new_values = {"$set": {"disabled": enable}}
        await users_collection.update_one(query, new_values)
        message = "Disconnected successfully" if enable else "Connected successfully"
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_users():
    try:
        users_dict = {}
        cursor = await users_collection.find().to_list(length=None)
        for user in cursor:
            users_dict[user["email"]] = {
                "id": user["_id"],
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "email": user["email"],
                "password": user["password"],
                "age": user["age"],
                "country": user["country"],
                "state": user["state"],
                "role": user["role"],
                "disabled": user["disabled"]
            }
        return users_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_question(question: Question):
    try:
        await questions_collection.insert_one(jsonable_encoder(question))
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_response(user_id: str):
    try:
        user_question = await questions_collection.find_one(
            {"userId": user_id},
            sort=[("date", -1)]
        )
        if not user_question:
            raise HTTPException(status_code=404, detail="Question not found")

        user_question_id = user_question["_id"]
        chat_response = model_response(user_question["question"])
        query = {"_id": user_question_id}
        new_values = {"$set": {"answer": chat_response}}
        await questions_collection.update_one(query, new_values)

        return {"_id": user_question_id, "response": chat_response,
                "question": user_question["question"], "userId": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_user_questions(user_id: str):
    try:
        history = []
        cursor = await questions_collection.find({"userId": user_id}).to_list(
            length=100)
        for question in cursor:
            question['_id'] = str(question['_id'])
            history.append(question)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_faq():
    try:
        all_faq = []
        cursor = await faq_collection.find().to_list(length=None)
        for question in cursor:
            question['_id'] = str(question['_id'])
            all_faq.append(question)
        return all_faq
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_faq(faq: FrequentlyAskedQuestion):
    try:
        await faq_collection.insert_one(jsonable_encoder(faq))
        return faq
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_faq(faq_id: str, faq: EditQuestion):
    try:
        query = {"_id": faq_id}
        new_faq = jsonable_encoder(faq)
        new_values = {"$set": {"question": new_faq["question"],
                               "answer": new_faq["answer"]}}
        response = await faq_collection.update_one(query, new_values)
        if response.matched_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"message": f"FAQ with ID {faq_id} updated successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


async def delete_faq(faq_id: str):
    try:
        query = {"_id": faq_id}
        response = await faq_collection.delete_one(query)
        if response.deleted_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"message": f"FAQ with ID {faq_id} deleted successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_active_users():
    try:
        query = {"disabled": False}
        response = await users_collection.count_documents(query)
        return {"activeUsers": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_total_questions():
    try:
        response = await questions_collection.count_documents({})
        return {"totalQuestions": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_users_by_age():
    try:
        users_by_age = {
            "0-18": 0,
            "19-30": 0,
            "31-50": 0,
            "51-65": 0,
            "66+": 0
        }
        cursor = await users_collection.find().to_list(length=None)
        for user in cursor:
            if 0 <= user["age"] <= 18:
                users_by_age["0-18"] += 1
            elif 19 <= user["age"] <= 30:
                users_by_age["19-30"] += 1
            elif 31 <= user["age"] <= 50:
                users_by_age["31-50"] += 1
            elif 51 <= user["age"] <= 65:
                users_by_age["51-65"] += 1
            else:
                users_by_age["66+"] += 1
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return [{"age": k, "count": v} for k, v in users_by_age.items()]


async def questions_by_day():
    try:
        pipeline = [
            {"$match": {
                "date": {"$regex": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"}}},
            {"$addFields": {"date_truncated": {"$substr": ["$date", 0, 19]}}},
            {"$addFields": {"date": {
                "$dateFromString": {"dateString": "$date_truncated",
                                    "format": "%Y-%m-%dT%H:%M:%S"}}}},
            {"$group": {"_id": {
                "$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                        "count": {"$sum": 1}}},
            {"$sort": {"_id": ASCENDING}}
        ]
        cursor = questions_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        formatted_result = [{"date": item["_id"], "count": item["count"]} for
                            item in result]
        return formatted_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
