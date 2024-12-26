import logging, re

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash
from flaskr.auth import moderator_login_required
from flaskr.db import get_db
bp = Blueprint('mod', __name__, url_prefix='/mod')

@bp.route('/home', methods=["GET"])
@moderator_login_required
def home():
    return render_template('mod/home.html')

@bp.route('/manage_moderators', methods=["GET"])
@moderator_login_required
def manage_moderators():
    db = get_db()

    error = ""

    try:
        current_app.logger.debug(f"SELECT * FROM user WHERE id != {g.user['id']} AND is_mod = 1")
        moderators = db.execute(f"SELECT * FROM user WHERE id != {g.user['id']} AND is_mod = 1").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(moderators)

    if error:
        flash(error)
        return redirect(url_for('mod.home'))

    return render_template('mod/manage_moderators.html', moderators=moderators)

@bp.route('/add_moderator', methods=["GET", "POST"])
@moderator_login_required
def add_moderator():
    db = get_db()
    error = ""

    if request.method == 'POST':
        try:
            current_app.logger.debug(f"UPDATE user SET is_mod = True WHERE id = {request.form['user_id']}")
            db.execute(
                f"UPDATE user SET is_mod = 1 WHERE id = {request.form['user_id']}"
            )
            db.commit()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error(error)
        else:
            current_app.logger.warning(f"Role of user whose id={request.form['user_id']} changes to Moderator")
            return redirect(url_for('mod.add_moderator'))
    
        if error:
            flash(error)
            return redirect(url_for('mod.home'))

    try:
        current_app.logger.debug(f"SELECT * FROM user WHERE id != {g.user['id']} AND is_mod = 0")
        users = db.execute(f"SELECT * FROM user WHERE id != {g.user['id']} AND is_mod = 0").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(users)
        return render_template('mod/add_moderator.html', users=users)

    if error:
        flash(error)
        return redirect(url_for('mod.home'))

@bp.route('/delete_moderator', methods=["GET", "POST"])
@moderator_login_required
def delete_moderator():
    db = get_db()
    error = ""

    if request.method == 'POST':
        try:
            current_app.logger.debug(f"DELETE FROM user WHERE id = {session['moderator_id']}")
            db.execute(
                f"DELETE FROM user WHERE id = {session['moderator_id']}"
            )
            db.commit()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error(error)
        else:
            del session["moderator_id"]
            flash("Moderator deleted successfully")
            return redirect(url_for('mod.manage_moderators'))

        if error:
            flash(error)
            return redirect(url_for('mod.home'))

    moderatorId = request.args.get("moderator_id")
    moderatorNickName = request.args.get("moderator_nickname")

    session["moderator_id"] = moderatorId

    return render_template('mod/delete_moderator.html', moderator_nick_name=moderatorNickName)

@bp.route('/manage_user_balances', methods=["GET", "POST"])
@moderator_login_required
def manage_user_balances():
    db = get_db()
    error = ''

    if request.method == "POST":
        try:
            current_app.logger.debug(f"UPDATE user SET joke_balance='{request.form['new_joke_balance']}' WHERE id = '{request.form['user_id']}'")
            db.execute(
                f"UPDATE user SET joke_balance='{request.form['new_joke_balance']}' WHERE id = '{request.form['user_id']}'"
            )
            db.commit()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error(error)
        else:
            flash("User balance changed successfully")
            return redirect(url_for('mod.manage_user_balances'))
        
        if error:
            flash(error)
            return redirect(url_for('mod.home'))

    try:
        current_app.logger.debug("SELECT * FROM user WHERE is_mod = 0")
        users = db.execute(f"SELECT * FROM user WHERE is_mod = 0").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(users)
        return render_template('mod/manage_user_balances.html', users=users)
    
    if error:
        flash(error)
        return redirect(url_for('mod.home'))

@bp.route('/manage_jokes', methods=["GET"])
@moderator_login_required
def manage_jokes():
    db = get_db()

    error = ""

    try:
        current_app.logger.debug("SELECT * FROM joke")
        jokes = db.execute("SELECT * FROM joke").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
    else:
        current_app.logger.debug(jokes)
        return render_template('mod/manage_jokes.html', jokes=jokes)
    
    if error:
        flash(error)
        return redirect(url_for('mod.home'))

@bp.route('/manage_logging', methods=["GET", "POST"])
@moderator_login_required
def manage_logging():
    if request.method == 'POST':
        for handler in current_app.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                if logging.getLevelName(handler.level) == 'INFO':
                    handler.setLevel(logging.DEBUG)
                    flash("Successfully Enabled DEBUG logging mode")
                else:
                    flash("Successfully Disabled DEBUG logging mode")
                    handler.setLevel(logging.INFO)

        return redirect(url_for('mod.home'))

    currentLevel = ''
    for handler in current_app.logger.handlers:
        if isinstance(handler, logging.FileHandler):
            currentLevel = logging.getLevelName(handler.level)

    return render_template('mod/manage_logging.html', current_level=currentLevel)
