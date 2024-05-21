from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
import os
from models import Question
from bson import ObjectId
from own_gpt import model_response
from dotenv import load_dotenv

load_dotenv()

client_url = os.getenv('ATLAS_URI')
database_name = os.getenv('DB_NAME')


client = AsyncIOMotorClient(client_url)
database = client[database_name]
questions_collection = database["questions"]
users_collection = database["neoris"]


async def create_question(question: Question):
    """
    Method to create a new question and associate it with a user
    :param question: Question to be created
    :return: User with the new question associated
    """
    try:
        # Insert the question into the database, collection "questions"
        await questions_collection.insert_one(jsonable_encoder(question))

        return question

    except Exception as e:
        return str(e)


async def get_response(user_id: str):
    """
    Method to get the response from the model
    :param user_id: User ID
    :return: Dictionary with the response and the question
    """
    try:
        # Find the most recent question from the user
        user_question = await questions_collection.find_one(
            {"userId": user_id},
            sort=[("date", -1)]
        )

        # Find the question ID
        user_question_id = user_question["_id"]

        # Obtain the response from the model
        chat_response = model_response(user_question["question"])

        # Create a query to find the question by its ID
        query = {"_id": user_question_id}
        # Create a new value to push the new answer to the question
        new_values = {"$set": {"answer": chat_response}}
        # Update the question with the new answer
        await questions_collection.update_one(query, new_values)

        return {"response": chat_response,
                "question": user_question["question"]}
    except Exception as e:
        return str(e)


async def get_user_questions(user_id: str):
    """
    Method to get all the questions and answers from a user
    :param user_id: User ID
    :return: A list with all the questions and answers from the user
    """
    try:
        history = []
        cursor = await questions_collection.find(
            {"userId": user_id}
        ).to_list(length=100)

        for question in cursor:
            question['_id'] = str(question['_id'])  # Convert ObjectId to string
            history.append(question)

        return history
    except Exception as e:
        return str(e)
