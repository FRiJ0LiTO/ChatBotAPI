from fastapi import APIRouter, Body, HTTPException, status, File, UploadFile, \
    Depends
from models import User as ModelUser, Question, FrequentlyAskedQuestion
from database import (create_user, get_all_users, create_question,
                      get_response,
                      get_user_questions, get_all_faq, create_faq, update_faq,
                      delete_faq)
import os
import shutil
from typing import Annotated
from bson import ObjectId
from auth import User, get_current_active_user

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome"}


@router.get("/users")
async def get_users(
        current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Method to get all the users from the database
    :param current_user: Current user making the request
    :return: A list with all the users
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await get_all_users()


@router.post("/question")
async def create_user_question(
        current_user: Annotated[User, Depends(get_current_active_user)],
        question: Question = Body(...)):
    """
    Method to create a new question in the database
    :param current_user: Current user making the request
    :param question: The question to be created
    :return: A message with the created question
    """
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await create_question(question)


@router.get("/response/{user_id}")
async def get_user_response(
        current_user: Annotated[User, Depends(get_current_active_user)],
        user_id: str):
    """
    Method to get the response of the chatbot to a user question
    :param current_user: Current user making the request
    :param user_id: ID of the user to get the response
    :return: A message with the response of the chatbot
    """
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await get_response(user_id)


@router.get("/history/{user_id}")
async def get_history(
        current_user: Annotated[User, Depends(get_current_active_user)],
        user_id: str):
    """
    Method to get all the questions and answers from a user
    :param current_user: Current user making the request
    :param user_id: ID of the user to get the history
    :return: A list with all the questions and answers from the user
    """
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await get_user_questions(user_id)


@router.get("/faqs/")
async def get_faqs():
    """
    Method to get all the FAQs from the database
    :return: A list with all the FAQs
    """
    return await get_all_faq()


@router.post("/faq/")
async def create_faq_question(
        current_user: Annotated[User, Depends(get_current_active_user)],
        faq: FrequentlyAskedQuestion = Body(...)):
    """
    Method to create a new FAQ in the database
    :param current_user: Current user making the request
    :param faq: The FAQ to be created
    :return: The created FAQ
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await create_faq(faq)


@router.put("/faq/{faq_id}")
async def update_faq_question(
        current_user: Annotated[User, Depends(get_current_active_user)],
        faq_id: str, faq: FrequentlyAskedQuestion = Body(...)):
    """
    Method to update a FAQ in the database
    :param current_user: Current user making the request
    :param faq_id: ID of the FAQ to be updated
    :param faq: Model with the new data for the FAQ
    :return: A message with the result of the operation
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await update_faq(faq_id, faq)


@router.delete("/faq/{faq_id}")
async def delete_faq_question(
        current_user: Annotated[User, Depends(get_current_active_user)],
        faq_id: str):
    """
    Method to delete a FAQ from the database
    :param current_user: Current user making the request
    :param faq_id: ID of the FAQ to be deleted
    :return: A message with the result of the operation
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    return await delete_faq(faq_id)


@router.post("/upload/")
async def upload_file(
        current_user: Annotated[User, Depends(get_current_active_user)],
        file: UploadFile):
    """
    Method to upload a file to the server
    :param current_user: Current user making the request
    :param file: Document to be uploaded
    :return: A message with the filename
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400,
                            detail="File must be a PDF file")
    try:
        # Open the file in the data folder with the same name as the file
        with open(os.path.join("../Neoris_API/data", file.filename),
                  "wb") as buffer:
            # Shutil is used to copy the file from the request to the buffer
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=str(e))


@router.delete("/delete/{filename}")
async def delete_file(current_user: Annotated[User, Depends(get_current_active_user)],
        filename: str):
    """
    Method to delete a file from the server
    :param current_user: Current user making the request
    :param filename: Name of the file to be deleted
    :return: Message with the file deleted
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You do not have the necessary permissions")
    try:
        os.remove(f"../Neoris_API/data/{filename}.pdf")
        return {"message": f"File {filename} deleted"}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=str(e))
