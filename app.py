import os

from flask import jsonify
from flask import session, request
from flask_socketio import emit, join_room
from requests import auth
from werkzeug.security import generate_password_hash, check_password_hash

from constants import POST, SUCCESS, ERROR, MESSAGE, SERVER_HOST, SERVER_PORT, CHATROOM, LOGIN, \
    REGISTER, PASSWORD, USERNAME, REPEATED_PASSWORD, GET_CHATROOMS, GET, JOIN_ROOM, SEND_MESSAGE, KEY_PATH, CERT_PATH
from models.messaging import Message, ChatRoom
from models.users import User
from utils import full_init_app, db, socketio, login_required, app

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
    session[USERNAME] = username


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
    join_room(chatroom)


@socketio.on(SEND_MESSAGE)
def on_send_message(data):
    username = data.get(USERNAME)
    chatroom = data.get(CHATROOM)
    message = data.get(MESSAGE)
    emit('message_received', {'username': 'System', 'message': f'{message}'},
         to=chatroom)
    return "bla test"











@login_required
@app.route('/send_message', methods=[POST])
def send_message():
    # use auth data for milestone 6
    auth = request.authorization
    if not auth:
        return jsonify({ERROR: 'Please add authorization.'}), 401
    username = auth.username
    if not username:
        return jsonify({ERROR: 'Username is required.'}), 401
    data = request.get_json()
    username = username.decode("utf-8") if isinstance(username, bytes) else username
    if MESSAGE not in data or CHATROOM not in data:
        return jsonify({ERROR: 'Message and chatroom are required.'}), 400

    message_text = data.get(MESSAGE)
    chatroom = data.get("chatroom")
    Message.message_to_db(username, message_text, chatroom)
    emit('message_received', {'username': username, 'message': message_text}, room=chatroom)

    return jsonify({SUCCESS: True}), 201

#
# @app.route('/get_messages', methods=[GET])
# def get_messages():
#     # use auth data for milestone 6
#     auth = request.authorization
#     if not auth:
#         return jsonify({ERROR: 'Please add authorization.'}), 401
#     username = auth.username
#     if not username:
#         return jsonify({ERROR: 'Username is required.'}), 401
#     username = username.decode("utf-8") if isinstance(username, bytes) else username
#     data = request.get_json()
#     if CHATROOM not in data:
#         return jsonify({ERROR: 'Chatroom is required.'}), 400
#
#     chatroom_name = data.get("chatroom")
#     user = User.get_or_create(username)
#
#     if db.session.query(ChatRoom.query.filter_by(name=chatroom_name).exists()).scalar():
#         messages = Message.get_all_unseen(username, chatroom_name)
#     else:
#         ChatRoom.chatroom_to_db(chatroom_name, user)
#         messages = list()
#     return jsonify(messages)
#


def run_server():
    host = os.environ.get(SERVER_HOST, 'localhost')
    port = os.environ.get(SERVER_PORT, 5000)
    socketio.run(app, host=host, port=port,  certfile=os.environ.get(CERT_PATH),
                 keyfile=os.environ.get(KEY_PATH), debug=True)


if __name__ == '__main__':
    run_server()
