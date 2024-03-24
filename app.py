import os
import ssl

from flask import Flask, jsonify, request

from models.messaging import Message, ChatRoom
from models.users import User
from models.utils import init_db, db
from constants import POST, GET, SUCCESS, ERROR, MESSAGE, SERVER_HOST, SERVER_PORT, FAIL_VALUE, GET_CHATROOMS, CHATROOM

app = Flask(__name__)
init_db(app)


def run_server():
    # Enable HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')

    host = os.environ.get(SERVER_HOST, '0.0.0.0')
    port = os.environ.get(SERVER_PORT, 5000)
    app.run(ssl_context=context, debug=True, host=host, port=port)


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

    return jsonify({SUCCESS: True}), 201


@app.route('/get_messages', methods=[GET])
def get_messages():
    # use auth data for milestone 6
    auth = request.authorization
    if not auth:
        return jsonify({ERROR: 'Please add authorization.'}), 401
    username = auth.username
    if not username:
        return jsonify({ERROR: 'Username is required.'}), 401
    username = username.decode("utf-8") if isinstance(username, bytes) else username
    data = request.get_json()
    if CHATROOM not in data:
        return jsonify({ERROR: 'Chatroom is required.'}), 400

    chatroom_name = data.get("chatroom")
    user = User.get_or_create(username)

    if db.session.query(ChatRoom.query.filter_by(name=chatroom_name).exists()).scalar():
        messages = Message.get_all_unseen(username, chatroom_name)
    else:
        ChatRoom.chatroom_to_db(chatroom_name, user)
        messages = list()
    return jsonify(messages)


@app.route(f'/{GET_CHATROOMS}', methods=[GET])
def get_chatrooms():
    result = ChatRoom.get_all_chatrooms()
    return jsonify(result)


if __name__ == '__main__':
    run_server()
