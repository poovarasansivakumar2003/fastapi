from utils import *
from routers.admin import get_current_user
from fastapi import status
from models import Todos

app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_todo(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]
    
def test_admin_read_all_users(test_user):
    response = client.get("/admin/user")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()[0]

    assert data['username'] == 'codingwithrobytest'
    assert data['email'] == 'codingwithrobytest@email.com'
    assert data['first_name'] == 'Eric'
    assert data['last_name'] == 'Roby'
    assert data['role'] == 'admin'
    assert data['phone_number'] == '(111)-111-1111'

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/9999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}

def test_admin_delete_user(test_user):
    response = client.delete("/admin/user/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model is None

def test_admin_delete_user_not_found():
    response = client.delete("/admin/user/9999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}