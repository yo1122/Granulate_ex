import os

from flask import jsonify
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from requests import auth
from werkzeug.security import generate_password_hash, check_password_hash

from constants import POST, SUCCESS, ERROR, MESSAGE, SERVER_HOST, SERVER_PORT, CHATROOM, LOGIN, \
    REGISTER, PASSWORD, USERNAME, REPEATED_PASSWORD, GET_CHATROOMS, GET, JOIN_ROOM, SEND_MESSAGE, KEY_PATH, CERT_PATH, \
    GET_MESSAGE, GET_MESSAGES
from models.messaging import Message, ChatRoom
from models.users import User
from utils import full_init_app, db, socketio, app

full_init_app()


def get_verified_data(request, require_auth=False, required_fields=None):
    auth_header = request.authorization
    data = request.get_json() if required_fields else dict()
    if require_auth:
        if not auth:
            return jsonify({ERROR: 'Please add authorization.'}), 401
        username = auth_header.username
        password = auth_header.password
        if not username:
            return jsonify({ERROR: 'Username is required.'}), 401
        username = username.decode("utf-8") if isinstance(username, bytes) else username
        data[USERNAME] = username
        data[PASSWORD] = password
    if required_fields:
        for field in required_fields:
            if field not in data:
                return jsonify({ERROR: f'{field} is required.'}), 400
    return data


def handle_login(username):
    # TODO: finish proper session handling
    session[USERNAME] = username


def authenticate_user(username):
    # TODO: use proper session handling, check password hash. Fetching user as future preparation
    user = User.query.filter_by(username=username).first()
    return bool(user)


@app.route(f'/{REGISTER}', methods=[POST])
def register():
    data = get_verified_data(request, require_auth=True, required_fields=[REPEATED_PASSWORD])
    username = data.get(USERNAME)
    password = data.get(PASSWORD)
    repeated_password = data.get(REPEATED_PASSWORD)

    if repeated_password == password:
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        handle_login(username)
        return jsonify({SUCCESS: True}), 201
    else:
        return jsonify({ERROR: "Passwords don't match."}), 401


@app.route(f'/{LOGIN}', methods=[POST])
def login():
    data = get_verified_data(request, require_auth=True)
    username = data.get(USERNAME)
    password = data.get(PASSWORD)

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        handle_login(username)
        return jsonify({SUCCESS: True}), 201
    else:
        return jsonify({ERROR: 'Invalid username/password combination.'}), 401


@app.route(f'/{GET_CHATROOMS}', methods=[GET])
def get_chatrooms():
    result = ChatRoom.get_all_chatrooms()
    return jsonify(result)


@socketio.on(JOIN_ROOM)
def handle_join_room(data):
    chatroom = data.get(CHATROOM)
    username = data.get(USERNAME)
    join_room(chatroom)

    if db.session.query(ChatRoom.query.filter_by(name=chatroom).exists()).scalar():
        messages = Message.get_all_unseen(username, chatroom)
        emit(GET_MESSAGES, {'username': username, 'message': messages})
    else:
        user = User.query.filter_by(username=username).first()
        ChatRoom.chatroom_to_db(chatroom, user)


@socketio.on('connect')
def test_connect(auth):
    username = auth.get(USERNAME)
    print(f'Client connected: {username}')
    # return false to reject unauthorized connections


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socketio.on_error_default
def default_error_handler(e):
    print(f'error: {e}')


@socketio.on('leave')
def on_leave(data):
    chatroom = data.get(CHATROOM)
    leave_room(chatroom)


@socketio.on(SEND_MESSAGE)
@socketio.on(MESSAGE)
def on_send_message(data):
    username = data.get(USERNAME)
    chatroom = data.get(CHATROOM)
    message = data.get(MESSAGE)
    if authenticate_user(username):
        emit(GET_MESSAGE, {'username': username, 'message': f'{message}'}, to=chatroom)
        Message.message_to_db(username, message, chatroom)
    else:
        sid = request.sid
        emit(ERROR, {'message': 'Unauthorized: User'}, to=sid)


def run_server():
    host = os.environ.get(SERVER_HOST, 'localhost')
    port = os.environ.get(SERVER_PORT, 5000)
    socketio.run(app, host=host, port=port,  certfile=os.environ.get(CERT_PATH),
                 keyfile=os.environ.get(KEY_PATH), debug=True)


if __name__ == '__main__':
    run_server()
