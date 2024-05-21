from fastapi import APIRouter, Body, HTTPException, status, File, UploadFile
from models import Question
from bson import ObjectId
from database import create_question, get_response, get_user_questions
import os
import shutil

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome"}


@router.post("/question")
async def create_user_question(question: Question = Body(...)):
    return await create_question(question)


@router.get("/response/{user_id}")
async def get_user_response(user_id: str):
    return await get_response(user_id)


@router.get("/history/{user_id}")
async def get_history(user_id: str):
    return await get_user_questions(user_id)


@router.post("/upload/")
async def upload_file(file: UploadFile):
    """
    Method to upload a file to the server
    :param file: Document to be uploaded
    :return: A message with the filename
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400,
                            detail="File must be a PDF file")
    try:
        # Open the file in the data folder with the same name as the file
        with open(os.path.join("../Neoris_API/data", file.filename), "wb") as buffer:
            # Shutil is used to copy the file from the request to the buffer
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=str(e))


@router.delete("/delete/{filename}")
async def delete_file(filename: str):
    """
    Method to delete a file from the server
    :param filename: Name of the file to be deleted
    :return: Message with the file deleted
    """
    try:
        os.remove(f"../Neoris_API/data/{filename}.pdf" )
        return {"message": f"File {filename} deleted"}
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=str(e))
