import os
from functools import wraps

from flask import Flask, Blueprint, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
db = SQLAlchemy()
socketio = SocketIO(app, cors_allowed_origins="*") #####

def get_db_uri():
    db_name = os.environ.get('MESSAGE_DB_NAME')
    db_host = os.environ.get('MESSAGE_DB_HOST', 'localhost')
    db_port = os.environ.get('MESSAGE_DB_PORT', 5432)
    db_username = os.environ.get('MESSAGE_DB_USER')
    db_password = os.environ.get('MESSAGE_DB_PASS')
    assert db_name and db_username and db_password
    return f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'


def full_init_app():
    socketio.init_app(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Set your secret key for SocketIO
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    try:
        with app.app_context():
            db.create_all()
    except OperationalError as e:
        print(f"Encountered an error creating DB tables. Make sure you've set up the DB and env vars: {e}")
        raise e
    #
    # main = Blueprint('main', __name__)
    # auth = Blueprint('auth', __name__)
    # app.register_blueprint(main)
    # app.register_blueprint(auth)
    return app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
