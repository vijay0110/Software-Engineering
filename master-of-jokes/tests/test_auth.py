import pytest
from flask import g, get_flashed_messages, session
from flaskr.db import get_db

# Invalid input for user registeration
@pytest.mark.parametrize(
    "email, nickname, password, message",
    [
        ("", "testuser", "password123", b'Email is required.'),  # Missing email
        ("test@example.com", "", "password123", b'Nickname is required.'),  # Missing nickname
        ("test@example.com", "testuser", "", b'Password is required.'),  # Missing password
        ("invalidemail", "testuser", "password123", b'Email Address format is incorrect.'),  # Invalid email format
        ("testuser@gmail.com", "testuser", "password123", b'The choosen email address or nickname is already registered.'),  # Existing nickname
    ]
)
def test_register_validate_input(client, email, nickname, password, message):
    with client:
        _ = client.post(
            '/auth/register',
            data={'email': email, 'nickname': nickname, 'password': password}
        )
        assert message == get_flashed_messages()[0].encode()

# Valid input for user registeration
def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'email': 'a@example.com', 'nickname': 'a', 'password': 'a'}
    )
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE nickname = 'a'",
        ).fetchone() is not None

# Invalid input for user login
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', 'test', b'Email or Nickname is required.'),
    ('a', '', b'Password is required.'),
    ('testuser', 'a', b'Incorrect password.'),
    ('testuser12', 'abcd', b'Incorrect username.'),
))
def test_login_validate_input(client, username, password, message):
    with client:
        _ = client.post('/auth/login', data={'username': username, 'password': password})
        assert message == get_flashed_messages()[0].encode()

# Valid input for user login
def test_login(client):
    assert client.get('/auth/login').status_code == 200

    with client:
        client.post('/auth/login', data={'username': 'testuser', 'password': 'abcd'})
        assert session['user_id'] == 1
        assert session['jokesVisited'] == []