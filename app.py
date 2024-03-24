import os
import ssl
from flask import Flask, jsonify, request
from constants import POST, GET, SUCCESS, ERROR, MESSAGE, SERVER_HOST, SERVER_PORT, FAIL_VALUE

app = Flask(__name__)

# Change to DB on milestone 3
messages = []


def run_server():
    # Enable HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')

    host = os.environ.get(SERVER_HOST, '0.0.0.0')
    port = os.environ.get(SERVER_PORT, 5000)
    app.run(ssl_context=context, debug=True, host=host, port=port)


def verify_incoming_message(request):
    # use auth data for milestone 6
    auth = request.authorization
    if not auth:
        return jsonify({ERROR: 'Please add authorization.'}), 401
    username = auth.username
    if not username:
        return jsonify({ERROR: 'Username is required.'}), 401
    data = request.get_json()
    if MESSAGE not in data:
        return jsonify({ERROR: 'Message is required.'}), 400
    return data, FAIL_VALUE


@app.route('/send_message', methods=[POST])
def send_message():
    data, code = verify_incoming_message(request)
    if code != FAIL_VALUE:
        return data, code

    username = request.authorization.username
    message = data[MESSAGE]
    messages.append({'username': username, MESSAGE: message})
    return jsonify({SUCCESS: True}), 201


@app.route('/get_messages', methods=[GET])
def get_messages():
    return jsonify(messages)


if __name__ == '__main__':
    run_server()
