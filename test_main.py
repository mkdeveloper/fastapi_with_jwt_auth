import pytest
from fastapi.testclient import TestClient
from main import app 
from decouple import config


client = TestClient(app)

def test_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the todo API"}

# Assuming the user is already logged in and the token is valid
Token = config("TOKEN")

headers = {"Authorization": "Bearer " + Token}

def test_create_todo():
    response = client.post("/todos", headers=headers, json={"title": "Test Todo", "description": "This is a test todo", "completed": False})
    assert response.status_code == 200
    assert response.json() == {"message": "Todo created successfully"}

def test_get_todos():
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_single_todo():
    response = client.get("/todos/8", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"

def test_update_todo():
    response = client.put("/todos/8", headers=headers, json={"title": "Updated Todo", "description": "This is an updated test todo", "completed": True})
    assert response.status_code == 200
    assert response.json() == {"message": "Todo updated successfully"}

def test_delete_todo():
    response = client.delete("/todos/8", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Todo deleted successfully"}

def test_get_nonexistent_todo():
    response = client.get("/todos/100", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_update_nonexistent_todo():
    response = client.put("/todos/100", headers=headers, json={"title": "Updated Todo", "description": "This is an updated test todo", "completed": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_delete_nonexistent_todo():
    response = client.delete("/todos/100", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_create_todo_with_invalid_data():
    response = client.post("/todos", headers=headers, json={"title": 12341234, "description": "This is a test todo"})
    assert response.status_code == 422
    # assert response.json() == {"detail": [{"loc": ["body", "completed"], "msg": "field required", "type": "value_error.missing"}]}


def test_update_todo_with_invalid_data():
    response = client.put("/todos/9", headers=headers, json={"title": 1234, "description": "This is a test todo", "completed": "finished"})
    assert response.status_code == 422
    # assert response.json() == {"detail": [{"loc": ["body", "completed"], "msg": "field required", "type": "value_error.missing"}]}

