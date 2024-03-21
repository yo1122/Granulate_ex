import ssl
from flask import Flask, jsonify, request
from constants import POST, GET, SUCCESS, ERROR, MESSAGE

app = Flask(__name__)

# Change to DB on milestone 3
messages = []


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
    if MESSAGE not in data:
        return jsonify({ERROR: 'Message is required.'}), 400

    message = data[MESSAGE]
    messages.append({'username': username, MESSAGE: message})
    return jsonify({SUCCESS: True}), 201


@app.route('/get_messages', methods=[GET])
def get_messages():
    return jsonify(messages)


if __name__ == '__main__':
    # Enable HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')

    app.run(ssl_context=context, debug=True)
