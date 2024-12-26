from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('joke', __name__, url_prefix='/joke')

@bp.route('/create', methods=["GET", "POST"])
@login_required
def create():
    db = get_db()

    error = ""
    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE author_id = {g.user['id']}")
        jokesOfCurrentUser = db.execute(f"SELECT * FROM joke WHERE author_id = {g.user['id']}").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(jokesOfCurrentUser)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            error = 'Title is required.'
        elif len(title.split(' ')) >= 11:
            error = 'Title contains more than 10 words.'
        else:
            for joke in jokesOfCurrentUser:
                if joke['title'] == title:
                    error = 'Title of Joke must be unique.'
                    break

            if error:
                current_app.logger.warning(error)
            else:
                try:
                    current_app.logger.debug(f"INSERT INTO joke (title, body, author_id, author_nickname) VALUES ({title}, {body}, {g.user['id']}, {g.user['nickname']})")
                    db.execute(
                        'INSERT INTO joke (title, body, author_id, author_nickname)'
                        ' VALUES (?, ?, ?, ?)',
                        (title, body, g.user['id'], g.user['nickname'])
                    )
                    db.commit()
                except db.OperationalError:
                    error = "Database Error! Unable to open database file"
                    current_app.logger.critical(error)
                except Exception:
                    error = "Database Error! Not able to perform database operation"
                    current_app.logger.error(error)
                else:
                    if session["jokeBalance"] == -1:
                        session["jokeBalance"] += 1
                    session["jokeBalance"] += 1
                    return redirect(url_for('joke.create'))

    if error:
        flash(error)

    if "jokeBalance" not in session:
        session["jokeBalance"] = g.user["joke_balance"]

    return render_template('joke/create.html', jokeBalance=session["jokeBalance"])

@bp.route("/my_jokes", methods=["GET"])
@login_required
def my_jokes():
    if "joke_id" in session:
        del session["joke_id"]

    db = get_db()

    error = ""
    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE author_id = {g.user['id']}")
        jokes = db.execute(f"SELECT * FROM joke WHERE author_id = {g.user['id']}").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(jokes)

    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    return render_template('joke/my_jokes.html', jokes=jokes, jokeCount=session["jokeBalance"])

@bp.route("/update", methods=["GET", "POST"])
@login_required
def update():
    db = get_db()

    error = ""
    if request.method == "POST":
        body = request.form['body']

        try:
            current_app.logger.debug(f"UPDATE joke SET body='{body}' WHERE id = '{session['joke_id']}'")
            db.execute(
                f"UPDATE joke SET body='{body}' WHERE id = '{session['joke_id']}'"
            )
            db.commit()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error(error)
        else:
            del session["joke_id"]
            return redirect(url_for('joke.my_jokes'))
        
        if error:
            flash(error)
            return redirect(url_for('joke.create'))

    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE id = '{request.args.get('joke_id')}'")
        jokes = db.execute(f"SELECT * FROM joke WHERE id = '{request.args.get('joke_id')}'").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(jokes)
        session['joke_id'] = request.args.get("joke_id")

    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    return render_template('joke/update.html', jokes=jokes)

@bp.route("/take", methods=["GET"])
@login_required
def take():
    if session["jokeBalance"] == 0 and not session["jokesVisited"]:
        flash('You need to first leave a joke.')
        return render_template('joke/create.html', jokeBalance=session["jokeBalance"])

    db = get_db()

    error = ""

    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE author_id != {g.user['id']}")
        jokes = db.execute(f"SELECT * FROM joke WHERE author_id != {g.user['id']}").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(jokes)

    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    return render_template('joke/take.html', jokes=jokes)

@bp.route("/view", methods=["GET"])
@login_required
def view():
    if session["jokeBalance"] == -1:
        flash('Your joke balance reached to 0. Please leave joke in order to view jokes.')
        return render_template('joke/create.html', jokeBalance=session["jokeBalance"])

    db = get_db()

    jokeId = request.args.get("joke_id")

    if jokeId not in session["jokesVisited"]:
        session["jokesVisited"].append(jokeId)
        session["jokeBalance"] -= 1
    
    error = ""

    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE id = {jokeId}")
        jokes = db.execute(f"SELECT * FROM joke WHERE id = {jokeId}").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error(error)
    else:
        current_app.logger.debug(jokes)
    
    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    return render_template('joke/view.html', jokes=jokes)

@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    db = get_db()

    if request.method == 'POST':
        try:
            current_app.logger.debug(f"DELETE FROM joke WHERE id = '{session['joke_id']}'")
            db.execute(
                f"DELETE FROM joke WHERE id = '{session['joke_id']}'"
            )
            db.commit()
        except db.OperationalError:
            error = "Database Error! Unable to open database file"
            current_app.logger.critical(error)
        except Exception:
            error = "Database Error! Not able to perform database operation"
            current_app.logger.error("Database Error! Not able to perform database operation")
        else:
            del session["joke_id"]
            return redirect(url_for('joke.my_jokes'))
        
        if error:
            flash(error)
            return redirect(url_for('joke.create'))

    jokeId = request.args.get("joke_id")

    session['joke_id'] = jokeId

    error = ""
    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE id = {jokeId}")
        jokes = db.execute(f"SELECT * FROM joke WHERE id = {jokeId}").fetchall()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error("Database Error! Not able to perform database operation")
    else:
        current_app.logger.debug(jokes)

    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    return render_template('joke/delete.html', jokes=jokes)

@bp.route("/rate", methods=["POST"])
@login_required
def rate():
    ratings = float(request.form["ratings"])
    jokeId = request.form["id"]

    db = get_db()

    error = ""
    try:
        current_app.logger.debug(f"SELECT * FROM joke WHERE id = {jokeId}")
        joke = db.execute(f"SELECT * FROM joke WHERE id = {jokeId}").fetchone()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error("Database Error! Not able to perform database operation")
    else:
        current_app.logger.debug(joke)

    if error:
        flash(error)
        return redirect(url_for('joke.create'))

    newRating = round((((joke["ratings"] * joke["number_of_rating"]) + round(ratings, 2)) / (joke["number_of_rating"] + 1)), 2)

    try:
        current_app.logger.debug(f"UPDATE joke SET ratings='{newRating}', number_of_rating='{joke['number_of_rating'] + 1}' WHERE id = '{jokeId}'")
        db.execute(
            f"UPDATE joke SET ratings='{newRating}', number_of_rating='{joke['number_of_rating'] + 1}' WHERE id = '{jokeId}'"
        )
        db.commit()
    except db.OperationalError:
        error = "Database Error! Unable to open database file"
        current_app.logger.critical(error)
    except Exception:
        error = "Database Error! Not able to perform database operation"
        current_app.logger.error("Database Error! Not able to perform database operation")
    else:
        return redirect(url_for('joke.view', joke_id=jokeId))
    
    if error:
        flash(error)
        return redirect(url_for('joke.create'))
