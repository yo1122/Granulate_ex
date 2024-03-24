import os
import threading

import requests
from socketio import Client

from constants import GET_CHATROOMS
from constants import LOGIN, REGISTER, ERROR, REPEATED_PASSWORD, USERNAME, PASSWORD, CHATROOM, JOIN_ROOM, \
    SERVER_HOST, SERVER_PORT

# TODO: handle ssl certificate smarter
# TODO: test db dockerfile
# TODO: go over all env vars and constants, especially if using const in several important places
# TODO: verify incoming message, especially format (unicode?)
# TODO: test per (main funcs/cases)

SERVER_URL = f"https://{os.environ.get(SERVER_HOST, 'localhost')}:{os.environ.get(SERVER_PORT, 5000)}"
socket_client = Client(ssl_verify=False)


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


def send_to_ws(event, data):
    socket_client.emit(event, data)


@socket_client.on('connect')
def on_connect():
    print('Connected to server')


@socket_client.event
def disconnect():
    print("Disconnected from server")








@socket_client.on('message_received')
def on_message(data):
    print(f"{data['username']}: {data['message']}")


def get_messages(username, chatroom):
    @socket_client.on('new_message')
    def handle_new_message(data):
        print(f"{data['username']}: {data['message']}")

    socket_client.connect(SERVER_URL)
    socket_client.emit('join', {"username": username, "chatroom": chatroom})


def send_message(stop_event, username, chatroom):
    while not stop_event.is_set():
        message = input("Enter your message: ")
        result = send_to_ws('send_message', {"username": username, "message": message, "chatroom": chatroom})
        print(f"result: {result}")
        # data = {"message": message, "chatroom": chatroom}
        # response = requests.post(f"{SERVER_URL}/send_message", json=data, auth=(username, ""), verify=False)
        # if response.status_code == 201:
        #     print("Message sent successfully.")
        # else:
        #     print("Failed to send message.")


def request_chatrooms():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


def start_all_components(username, password, chatroom):
    socket_client.connect(SERVER_URL, auth={USERNAME: username, PASSWORD: password})
    send_to_ws(JOIN_ROOM, {CHATROOM: chatroom})

    stop_event = threading.Event()
    send_message_thread = threading.Thread(target=send_message, args=(stop_event, username, chatroom))
    send_message_thread.start()

    return send_message_thread, stop_event

def run_client():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    if handle_auth(username, password):
        request_chatrooms()
        chatroom = input("Type name of existing or new chatroom to connect to: ")

        send_message_thread, stop_event = start_all_components(username, password, chatroom)

        try:
            socket_client.wait()
            send_message_thread.join()
        except KeyboardInterrupt:
            print("\nExiting...")
            socket_client.disconnect()
            stop_event.set()


if __name__ == "__main__":
    run_client()
