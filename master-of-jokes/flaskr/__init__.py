import logging
import os
import sys

from flask import Flask, redirect, url_for


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    log_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)  # Ensure log directory exists
    log_file = os.path.join(log_dir, 'app.log')

    # File handler
    formatter = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(formatter)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARN)
    console_formatter = logging.Formatter(formatter)
    console_handler.setFormatter(console_formatter)

    # Attach handlers to the app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.WARN)

    app.logger.info("Master Of Jokes App Startup!")
    app.logger.info("Executing Initialization Steps........")
    app.logger.info("1. Database File Path Configuration")
    app.logger.info(f"Default Database Configuration File Path: {os.path.join(app.instance_path, 'flaskr.sqlite')}")
    app.logger.info("2. Log File Path Configuration")
    app.logger.info(f"Default Log File Path: {os.path.join(log_dir, 'app.log')}")
    app.logger.info("3. Adding Handlers to logging object")

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.logger.info("4. Load the instance configuration from 'config.py' file")
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.logger.info(f"4. Load the test configuration {test_config}")
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def homepage():
        return redirect(url_for('auth.login'))

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import joke
    app.register_blueprint(joke.bp)

    from . import mod
    app.register_blueprint(mod.bp)

    return app