import requests
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import time

load_dotenv()

ENDPOINT = 'https://neorisprueba.onrender.com/api/v1'
LOCAL = 'http://localhost:8000/api/v1'

client_url = os.getenv('ATLAS_URI')
database_name = os.getenv('DB_NAME')

client = AsyncIOMotorClient(client_url)
database = client[database_name]
questions_collection = database["questions"]
users_collection = database["neoris"]


async def get_recent_register(user_id: str):
    """
    Method to get the most recent question from a user or answer
    from the chatbot
    :param user_id: User ID
    :return: Dictionary with the most recent question or answer
    """
    response = await questions_collection.find_one(
        {"userId": user_id},
        sort=[("date", -1)]
    )
    return response


def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_can_create_question():
    payload = {
        "question": "Qué hace NEORIS?",
        "userId": "82d00a97-d923-4c5a-bc8e-e1684eff66a9"
    }
    create_question_response = requests.post(f'{ENDPOINT}/question',
                                             json=payload)
    assert create_question_response.status_code == 200
    data = create_question_response.json()

    question_user = await get_recent_register(user_id=payload['userId'])

    assert data['_id'] == question_user['_id']
    assert data['question'] == question_user['question']
    assert data['userId'] == question_user['userId']


@pytest.mark.asyncio(scope="session")
async def test_can_get_response():
    user_id = "82d00a97-d923-4c5a-bc8e-e1684eff66a9"
    response = requests.get(f'{ENDPOINT}/response/{user_id}')
    assert response.status_code == 200

    data = response.json()

    response_chatbot = await get_recent_register(user_id=user_id)

    assert data['_id'] == response_chatbot['_id']
    assert data['response'] == response_chatbot['answer']
    assert data['question'] == response_chatbot['question']
    assert data['userId'] == response_chatbot['userId']


def test_can_get_user_history():
    user_id = "664c3ad9a7cab405d3c59696"
    response = requests.get(f'{ENDPOINT}/history/{user_id}')
    assert response.status_code == 200
    data = response.json()

    if len(data) > 0:
        assert data[0]['userId'] == user_id
        assert data[-1]['userId'] == user_id
    else:
        pytest.skip("No data available")


def test_can_upload_file():
    with open('test.pdf', 'rb') as file:
        response = requests.post(f'{LOCAL}/upload/',
                                 files={'file': file})
        assert response.status_code == 200
        data = response.json()
        assert data['filename'] == 'test.pdf'


def test_exists_file():
    assert os.path.exists('../data/test.pdf')


def test_can_delete_file():
    response = requests.delete(f'{LOCAL}/delete/test')
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'File test deleted'


def test_not_exists_file():
    assert not os.path.exists('../data/test.pdf')
