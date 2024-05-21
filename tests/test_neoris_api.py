import requests
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = 'https://neorisprueba.onrender.com/api/v1'

client_url = os.getenv('ATLAS_URI')
database_name = os.getenv('DB_NAME')


client = AsyncIOMotorClient(client_url)
database = client[database_name]
questions_collection = database["questions"]
users_collection = database["neoris"]


def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_can_create_question():
    payload = {
        "question": "Qué hace NEORIS?",
        "userId": "82d00a97-d923-4c5a-bc8e-e1684eff66a9"
    }
    create_question_response = requests.post(f'{ENDPOINT}/question',
                                             json=payload)
    assert create_question_response.status_code == 200
    data = create_question_response.json()

    async def get_question_user():
        response = await questions_collection.find_one(
            {"userId": payload["userId"]},
            sort=[("date", -1)]
        )
        return response

    question_user = await get_question_user()

    assert data['_id'] == question_user['_id']
    assert data['question'] == question_user['question']
    assert data['userId'] == question_user['userId']


def test_can_get_response():
    user_id = ""
    response = requests.get(f'{ENDPOINT}/response/{user_id}')
    assert response.status_code == 200

