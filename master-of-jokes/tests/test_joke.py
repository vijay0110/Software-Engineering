import pytest
from flaskr.db import get_db
from flask import g, get_flashed_messages, session

# Create Joke
def test_create_joke(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'Test Joke', 'body': 'This is a test joke'})
        assert session['jokeBalance'] == 1

# Invalid input for joke creation --> (Title contains more than 10 words)
def test_create_joke_invalid_title(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'A ' * 11, 'body': 'This is a test joke'})
        assert b'Title contains more than 10 words.' in get_flashed_messages()[0].encode()

# Invalid input for joke creation --> (Title contains more than 10 words)
def test_create_joke_duplicate_title(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'Duplicate Joke', 'body': 'This is a test joke'})
        auth_client.post('/joke/create', data={'title': 'Duplicate Joke', 'body': 'Another test joke'})
        assert b'Title of Joke must be unique.' in get_flashed_messages()[0].encode()

# Validate whether 'my_jokes' page renders or not
def test_my_jokes(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'My Joke', 'body': 'This is my joke'})
        response = auth_client.get('/joke/my_jokes')
        assert b'My Joke' in response.data

# Validate update descripton of joke
def test_update_joke(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'Update Joke', 'body': 'Original body'})
        joke = get_db().execute('SELECT * FROM joke WHERE title = ?', ('Update Joke',)).fetchone()
        
        auth_client.get(f'/joke/update?joke_id={joke["id"]}')
        response = auth_client.post(f'/joke/update?joke_id={joke["id"]}', data={'body': 'Updated body'})
        assert response.status_code == 302

        updated_joke = get_db().execute('SELECT * FROM joke WHERE id = ?', (joke['id'],)).fetchone()
        assert updated_joke['body'] == 'Updated body'

# Validate deletion of joke
def test_delete_joke(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        auth_client.post('/joke/create', data={'title': 'Delete Joke', 'body': 'This joke will be deleted'})
        joke = get_db().execute('SELECT * FROM joke WHERE title = ?', ('Delete Joke',)).fetchone()
        
        auth_client.get(f'/joke/delete?joke_id={joke["id"]}')
        response = auth_client.post(f'/joke/delete?joke_id={joke["id"]}')
        assert response.status_code == 302

        deleted_joke = get_db().execute('SELECT * FROM joke WHERE id = ?', (joke['id'],)).fetchone()
        assert deleted_joke is None

# Validate whether view joke page renders or not
def test_view_joke(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        joke = get_db().execute('SELECT * FROM joke WHERE title = ?', ('A Test Joke',)).fetchone()

        response = auth_client.get(f'/joke/view?joke_id={joke["id"]}')
        assert b'A Test Joke' in response.data
        assert b'A Test Joke Body' in response.data

# Validate joke balance after creating a joke
def test_joke_balance(auth_client):
    with auth_client:
        _ = auth_client.get('/joke/create')
        initial_balance = session['jokeBalance']
        auth_client.post('/joke/create', data={'title': 'Balance Test', 'body': 'Testing joke balance'})
        assert session['jokeBalance'] == initial_balance + 1

        other_user_joke = get_db().execute('INSERT INTO joke (title, body, author_id, author_nickname) VALUES (?, ?, ?, ?)',
                                        ('Balance Joke', 'This joke affects balance', 2, 'otheruser')).lastrowid
        get_db().commit()

        auth_client.get(f'/joke/view?joke_id={other_user_joke}')
        assert session['jokeBalance'] == initial_balance

# Test unauthorized access of page
def test_unauthorized_access(client):
    # Accessing joke pages without logged in
    response = client.get('/joke/create')
    assert response.status_code == 302
    assert b'Redirecting' in response.data
    assert b'/auth/login' in response.data

    response = client.get('/joke/my_jokes')
    assert response.status_code == 302
    assert b'Redirecting' in response.data
    assert b'/auth/login' in response.data

    response = client.get('/joke/take')
    assert response.status_code == 302
    assert b'Redirecting' in response.data
    assert b'/auth/login' in response.data
        