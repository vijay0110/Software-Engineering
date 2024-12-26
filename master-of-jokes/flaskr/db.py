import functools
import sqlite3
from datetime import datetime

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash

def log_entry_exit(func):
    """
    Decorator to log the entry and exit of a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_app.logger.debug(f"Entering function: '{func.__name__}'")
        result = func(*args, **kwargs)
        current_app.logger.debug(f"Exiting function: '{func.__name__}'")
        return result
    return wrapper

@log_entry_exit
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

@log_entry_exit
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@log_entry_exit
def init_db():
    db = get_db()

    try:
        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
    except FileNotFoundError:
        current_app.logger.error("Not able to find database schema file")
    else:
        current_app.logger.info("Initialized the database.")
        click.echo('Initialized the database.')


@click.command('init-db')
@log_entry_exit
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()

@click.command('init-moderator')
@log_entry_exit
def init_moderator_command():
    """Create a user in the database and set that user role is equal to moderator"""
    db = get_db()

    email = 'team4@gmail.com'
    nickname = 'teamModAccount'
    password = 'team4'

    try:
        current_app.logger.debug(f"INSERT INTO user (email, nickname, password, joke_balance, is_mod) VALUES ({email}, {nickname}, {generate_password_hash(password)}, 0, True)")
        db.execute(
            'INSERT INTO user (email, nickname, password, joke_balance, is_mod)'
            ' VALUES (?, ?, ?, ?, ?)',
            (email, nickname, generate_password_hash(password), 0, True)
        )
        db.commit()
    except db.OperationalError:
            current_app.logger.critical("Database Error! Unable to open database file")
    except Exception:
        current_app.logger.error("Database Error! Not able to perform database operation")
    else:
        current_app.logger.info("Moderator Initialization is Successful.")
        click.echo('Moderator Initialization is Successful.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_moderator_command)