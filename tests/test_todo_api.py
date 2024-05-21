import requests

ENDPOINT = 'https://todo.pixegami.io'


def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


def test_can_create_task():
    payload = {
        "content": "Laundry",
        "user_id": "test_user",
        "task_id": "test_task_id",
        "is_done": False
    }
    create_task_response = requests.put(f'{ENDPOINT}/create-task', json=payload)
    assert create_task_response.status_code == 200

    data = create_task_response.json()
    print(data)

    task_id = data['task']['task_id']
    get_task_response = requests.get(f'{ENDPOINT}/get-task/{task_id}')

    assert get_task_response.status_code == 200
    get_task_data = get_task_response.json()
    assert get_task_data['content'] == payload['content']
    assert get_task_data['user_id'] == payload['user_id']
    assert get_task_data['task_id'] == data['task']['task_id']
