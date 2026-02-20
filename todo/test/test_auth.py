from utils import *
from routers.auth import authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'

def test_create_user(test_user):
    request_data={
        'username' : 'codingwithrobytest1',
        'email' : 'codingwithrobytest@egmail.com',
        'first_name' : 'Eric',
        'last_name' : 'Roby',
        'password' : 'testpassword',
        'role' : 'admin',
        'phone_number' : '(111)-111-1111'
    }

    response = client.post('/auth', json=request_data)
    assert response.status_code == 201
    
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.username == request_data["username"]).first()
    
    assert model.username == request_data.get('username')
    assert model.email == request_data.get('email')
    assert model.first_name == request_data.get('first_name')
    assert model.last_name == request_data.get('last_name')
    assert bcrypt_context.verify(request_data.get('password'), model.hashed_password)
    assert model.role == request_data.get('role')
    assert model.phone_number == request_data.get('phone_number')
    