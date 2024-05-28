from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
import os
from models import User, Question, FrequentlyAskedQuestion, EditQuestion
from own_gpt import model_response
from dotenv import load_dotenv
from passlib.context import CryptContext
from pymongo.errors import PyMongoError

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
    """
    Method to create a new user
    :param user: User to be created
    :return: User created
    """
    try:
        # Hash the password
        user.password = get_password_hash(user.password)
        # Insert the user into the database, collection "neoris"
        await users_collection.insert_one(jsonable_encoder(user))

        return user
    except Exception as e:
        return str(e)


async def get_all_users():
    """
    Method to get all the questions and answers from a user
    :return: A list with all the questions and answers from the user
    """
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
        return str(e)


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

        return {"_id": user_question_id,
                "response": chat_response,
                "question": user_question["question"],
                "userId": user_id}
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


async def get_all_faq():
    """

    :return:
    """
    try:
        all_faq = []
        cursor = await faq_collection.find().to_list(length=None)

        for question in cursor:
            question['_id'] = str(
                question['_id'])  # Convert ObjectId to string
            all_faq.append(question)

        return all_faq
    except Exception as e:
        return str(e)


async def create_faq(faq: FrequentlyAskedQuestion):
    """
    Creates a new FAQ document in the collection.

    :param faq: The FAQ object to be created.
    :return: The created FAQ object or an error message.
    """
    try:
        await faq_collection.insert_one(jsonable_encoder(faq))
        return faq
    except PyMongoError as e:
        return {"error": str(e)}


async def update_faq(faq_id: str, faq: EditQuestion):
    """
    Updates an existing FAQ document with new data.
    :param faq_id: The ID of the FAQ to be updated.
    :param faq: The new FAQ data.
    :return: The update result or an error message.
    """
    try:
        query = {"_id": faq_id}
        new_faq = jsonable_encoder(faq)
        new_values = {
            "$set": {"question": new_faq["question"], "answer": new_faq["answer"]}
        }
        response = await faq_collection.update_one(query, new_values)
        if response.matched_count == 0:
            return {"error": "FAQ not found"}
        return {"message": f"FAQ with ID {faq_id} updated successfully"}
    except PyMongoError as e:
        return {"error": str(e)}


async def delete_faq(faq_id: str):
    """
    Deletes an existing FAQ document.

    :param faq_id: The ID of the FAQ to be deleted.
    :return: The delete result or an error message.
    """
    try:
        query = {"_id": faq_id}
        response = await faq_collection.delete_one(query)
        if response.deleted_count == 0:
            return {"error": "FAQ not found"}
        return {"message": f"FAQ with ID {faq_id} deleted successfully"}
    except PyMongoError as e:
        return {"error": str(e)}

