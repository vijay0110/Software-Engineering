import logging
from flaskr.db import get_db

# Access to moderator home page
def test_moderator_home_access(auth_moderator):
    response = auth_moderator.get('/mod/home')
    assert response.status_code == 200
    assert b'Moderator Action Page' in response.data

# Unauthorized Access to moderator home page
def test_non_moderator_home_access(auth_client):
    response = auth_client.get('/mod/home')
    assert response.status_code == 302
    assert b'Redirecting' in response.data

# Managing moderators (viewing, adding, and deleting)
def test_manage_moderators(auth_moderator):
    response = auth_moderator.get('/mod/manage_moderators')
    assert response.status_code == 200
    assert b'Moderators List' in response.data

def test_add_moderator(auth_moderator, app):
    response = auth_moderator.post('/mod/add_moderator', data={'user_id': 1})
    assert response.status_code == 302
    
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = 1').fetchone()
        assert user['is_mod'] == 1

def test_delete_moderator(auth_moderator, app):
    _ = auth_moderator.get('/mod/delete_moderator?moderator_id=2&moderator_nickname=testmoderator')
    response = auth_moderator.post('/mod/delete_moderator')
    assert response.status_code == 302
    
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = 2').fetchone()
        assert user is None

# Managing user balances
def test_manage_user_balances(auth_moderator):
    response = auth_moderator.get('/mod/manage_user_balances')
    assert response.status_code == 200
    assert b"User's joke balance" in response.data

# Updating user balances
def test_update_user_balance(auth_moderator, app):
    response = auth_moderator.post('/mod/manage_user_balances', data={'user_id': 1, 'new_joke_balance': 10})
    assert response.status_code == 302
    
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = 1').fetchone()
        assert user['joke_balance'] == 10

# Managing jokes
def test_manage_jokes(auth_moderator):
    response = auth_moderator.get('/mod/manage_jokes')
    assert response.status_code == 200
    assert b'Joke List' in response.data

# Managing logging settings
def test_manage_logging(auth_moderator):
    response = auth_moderator.get('/mod/manage_logging')
    assert response.status_code == 200
    assert b'Enable/Disable debug' in response.data

def test_toggle_debug_logging(auth_moderator, app):
    _ = auth_moderator.get('/mod/manage_logging')
    response = auth_moderator.post('/mod/manage_logging')
    assert response.status_code == 302
    
    for handler in app.logger.handlers:
        if isinstance(handler, logging.FileHandler):
            assert handler.level == logging.DEBUG

# Unauthorized access attempts
def test_unauthorized_access(client):
    response = client.get('/mod/home')
    assert response.status_code == 302
    assert b'Redirecting' in response.data

# Database error handling
def test_database_error_handling(auth_moderator, app):
    with app.app_context():
        db = get_db()
        db.execute("DROP TABLE user")
        db.commit()
    
    response = auth_moderator.get('/mod/manage_moderators')
    assert response.status_code == 302
    assert b'Redirecting' in response.data