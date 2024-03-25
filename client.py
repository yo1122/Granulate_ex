import os
import time

import requests
import socketio
from socketio import Client

from constants import GET_CHATROOMS, MESSAGE, GET_MESSAGE, GET_MESSAGES
from constants import LOGIN, REGISTER, ERROR, REPEATED_PASSWORD, USERNAME, PASSWORD, CHATROOM, JOIN_ROOM, \
    SERVER_HOST, SERVER_PORT

# TODO: handle ssl certificate smarter
# TODO: go over all env vars and constants, especially if using const in several important places
# TODO: verify incoming message, especially format (unicode?)
# TODO: test per (main funcs/cases)

SERVER_URL = f"https://{os.environ.get(SERVER_HOST, 'localhost')}:{os.environ.get(SERVER_PORT, 5000)}"
socket_client = Client(ssl_verify=False)
connection_data = {}  # Bad practice, due to lack of time


def send_request(endpoint, is_get=False, data=None, username=None, password=None):
    headers = {'Content-Type': 'application/json'}
    if is_get:
        return requests.get(f"{SERVER_URL}/{endpoint}", verify=False)
    elif username and password:
        if data:
            return requests.post(f"{SERVER_URL}/{endpoint}", json=data, auth=(username, password), headers=headers,
                                 verify=False)
        else:
            return requests.post(f"{SERVER_URL}/{endpoint}", auth=(username, password), headers=headers,
                                 verify=False)


def show_user_message(username, message):
    print(f"{username}: {message}")


def send_to_ws(event, data):
    socket_client.emit(event, data)


def reconnect():
    print("Attempting to reconnect...")
    time.sleep(2)
    send_to_ws(JOIN_ROOM, {USERNAME: connection_data[USERNAME], CHATROOM: connection_data[CHATROOM]})


@socket_client.on('connect')
def on_connect():
    print('Connected to server')
    send_to_ws(JOIN_ROOM, {USERNAME: connection_data[USERNAME], CHATROOM: connection_data[CHATROOM]})


@socket_client.event
def disconnect():
    print("Disconnected from server")


@socket_client.event
def connect_error(data):
    print(f"Connection failed: {data}")


@socket_client.on(ERROR)
def on_error(data):
    error_message = data.get('message')
    print(f"Received error from server: {error_message}")


@socket_client.on(GET_MESSAGE)
def on_message(data):
    show_user_message(data[USERNAME], data[MESSAGE])


@socket_client.on(GET_MESSAGES)
def on_messages(data):
    if data.get(MESSAGE):
        print("You missed the following messages while gone:")
        for message in data[MESSAGE]:
            show_user_message(message[USERNAME], message[MESSAGE])


def request_chatrooms():
    response = send_request(GET_CHATROOMS, is_get=True)
    if response.status_code == 200:
        chatrooms = response.json()
        print(f"Available chatrooms: {', '.join(chatrooms)}")
    else:
        print("Failed to fetch chat rooms.")


def handle_auth(username, password):
    response = send_request(LOGIN, username=username, password=password)
    if response.status_code == 201:
        print(f"Successfully logged in {username}.")
        return True
    else:
        print(response.json()[ERROR])
        repeated_password = input("If you'd like to register - retype your password: ")
        data = {REPEATED_PASSWORD: repeated_password}
        response = send_request(REGISTER, data=data, username=username, password=password)
        if response.status_code == 201:
            return True
        else:
            if response.status_code == 401:
                print(response.json()[ERROR])
            else:
                print(f"Failed registration. Please try again later")
            return False


def safe_disconnect():
    # TODO: add 'finally' clause to run_client
    pass


def run_main_loop(username, password, chatroom):
    socket_client.connect(SERVER_URL, auth={USERNAME: username, PASSWORD: password, 'reconnection': True,
                                            'reconnection_attempts': 3, 'reconnection_delay': 1000,
                                            'reconnection_delay_max': 5000, 'randomization_factor': 0.5})

    send_to_ws(JOIN_ROOM, {USERNAME: username, CHATROOM: chatroom})

    while True:
        message = input("Enter your message: ")
        send_to_ws(MESSAGE, {"username": username, "message": message, "chatroom": chatroom})


def run_client():
    global connection_data  # bad practice, due to lack of time

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    if handle_auth(username, password):
        request_chatrooms()
        chatroom = input("Type name of existing or new chatroom to connect to: ")
        connection_data = {USERNAME: username, CHATROOM: chatroom}
        # handle socketio.exceptions.AuthenticationError
        try:
            run_main_loop(username, password, chatroom)
        except KeyboardInterrupt:
            print("\nExiting...")
        except socketio.exceptions.ConnectionError:
            print("\nFailed to connect, try again later...")


if __name__ == "__main__":
    run_client()
