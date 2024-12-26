import functools, re
import uuid

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not nickname:
            error = 'Nickname is required.'
        elif not password:
            error = 'Password is required.'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error = "Email Address format is incorrect."

        if error is None:
            try:
                current_app.logger.debug(f"INSERT INTO user (email, nickname, password) VALUES ({email}, {nickname}, {generate_password_hash(password)})")
                db.execute(
                    "INSERT INTO user (email, nickname, password) VALUES (?, ?, ?)",
                    (email, nickname, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"The choosen email address or nickname is already registered."
                current_app.logger.warning(error)
            except db.OperationalError:
                error = "Database Error! Unable to open database file"
                current_app.logger.critical(error)
            except Exception:
                error = "Database Error! Not able to perform database operation"
                current_app.logger.error(error)
            else:
                return redirect(url_for("auth.login"))
        else:
            current_app.logger.warning(error)

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "Email or Nickname is required."
        elif not password:
            error = "Password is required."
        else:
            try:
                current_app.logger.debug(f"SELECT * FROM user WHERE email = {username}")
                user = db.execute(
                    'SELECT * FROM user WHERE email = ?', (username,)
                ).fetchone()
            except db.OperationalError:
                error = "Database Error! Unable to open database file"
                current_app.logger.critical(error)
            except Exception:
                error = "Database Error! Not able to perform database operation"
                current_app.logger.error(error)
            else:
                current_app.logger.debug(user)

            if user is None:
                try:
                    current_app.logger.debug(f"SELECT * FROM user WHERE nickname = {username}")
                    user = db.execute(
                        'SELECT * FROM user WHERE nickname = ?', (username,)
                    ).fetchone()
                except db.OperationalError:
                    error = "Database Error! Unable to open database file"
                    current_app.logger.critical(error)
                except Exception:
                    error = "Database Error! Not able to perform database operation"
                    current_app.logger.error(error)
                else:
                    current_app.logger.debug(user)

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                session['jokesVisited'] = []
                current_app.logger.info(f"Authentication Successful for user with id={user['id']}")

                # TRUE (1) -> Moderator, FALSE (0) -> User
                if user['is_mod']:
                    return redirect(url_for('mod.home'))
                else:
                    return redirect(url_for('joke.create'))
            else:
                current_app.logger.warning(error)

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    # Logging steps
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    request.environ["SESSION_ID"] = session_id
    current_app.logger.debug(f"Request: Session ID={session_id}")
    current_app.logger.info(f"Request: Method={request.method}, URL={request.path}, Page Label={request.endpoint}")

    user_id = session.get('user_id')

    error = ""
    if user_id is None:
        g.user = None
    else:
        try:
            db = get_db()
            current_app.logger.debug(f"SELECT * FROM user WHERE id = {user_id}")
            g.user = db.execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error(error)
        else:
            current_app.logger.debug(g.user)

    if error:
        flash(error)
        return redirect(url_for('auth.login'))

@bp.after_app_request
def log_status_code(response):
    if response.status_code != 200:
        current_app.logger.warning(
            f"Request to {request.path} returned status code {response.status_code}."
        )
    current_app.logger.info(
        f"Request to {request.path} returned status code {response.status_code}."
    )
    return response

@bp.route('/logout')
def logout():
    db = get_db()
    
    if not g.user['is_mod']:
        try:
            current_app.logger.debug(f"UPDATE user SET joke_balance = {session['jokeBalance']} WHERE id = {session['user_id']}")
            db.execute(f"UPDATE user SET joke_balance = {session['jokeBalance']} WHERE id = {session['user_id']}")
            db.commit()
        except db.OperationalError:
            current_app.logger.critical("Database Error! Unable to open database file")
        except Exception:
            current_app.logger.error("Database Error! Not able to perform database operation")

    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        if g.user['is_mod']:
            current_app.logger.warning("Authorization Failure! Not Authorized to access this page.")
            return redirect(url_for('mod.home'))
        else:
            current_app.logger.info("Authorization Success! Authorized to access this page.")

        return view(**kwargs)

    return wrapped_view

def moderator_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        if not g.user['is_mod']:
            current_app.logger.warning("Authorization Failure! Not Authorized to access this page.")
            return redirect(url_for('joke.create'))
        else:
            current_app.logger.info("Authorization Success! Authorized to access this page.")

        return view(**kwargs)

    return wrapped_view