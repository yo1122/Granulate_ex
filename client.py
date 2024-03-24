import os

import requests
import threading
import time
from constants import POLL_TIME, SERVER_HOST, SERVER_PORT, GET_CHATROOMS

SERVER_URL = f"https://{os.environ.get(SERVER_HOST, '0.0.0.0')}:{os.environ.get(SERVER_PORT, 5000)}"

# TODO: handle ssl certificate smarter
# TODO: test db dockerfile
# TODO: go over all env vars and constants, especially if using const in several important places
# TODO: verify incoming message, especially format (unicode?)
# TODO: test per (main funcs/cases)


def get_messages(stop_event, username, chatroom):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #  WARNING: Verify false for debug only
    print("Messages:")
    while not stop_event.is_set():
        data = {"chatroom": chatroom}
        response = requests.get(f"{SERVER_URL}/get_messages", json=data, auth=(username, ""),verify=False)
        if response.status_code == 200:
            messages = response.json()
            for message in messages:
                print(f"{message['username']}: {message['message']}")
        else:
            print("Failed to fetch messages.")
        time.sleep(POLL_TIME)


def send_message(stop_event, username, chatroom):
    #  WARNING: Verify false for debug only

    while not stop_event.is_set():
        message = input("Enter your message: ")
        data = {"message": message, "chatroom": chatroom}
        response = requests.post(f"{SERVER_URL}/send_message", json=data, auth=(username, ""), verify=False)
        if response.status_code == 201:
            print("Message sent successfully.")
        else:
            print("Failed to send message.")


def request_chatrooms():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(f"{SERVER_URL}/{GET_CHATROOMS}", verify=False)
    if response.status_code == 200:
        chatrooms = response.json()
        print(f"Available chatrooms: {', '.join(chatrooms)}")
    else:
        print("Failed to fetch chat rooms.")


def start_all_threads(username, chatroom):
    stop_event = threading.Event()
    get_messages_thread = threading.Thread(target=get_messages, args=(stop_event, username, chatroom))
    send_message_thread = threading.Thread(target=send_message, args=(stop_event, username, chatroom))
    get_messages_thread.start()
    send_message_thread.start()
    return get_messages_thread, send_message_thread, stop_event

def run_client():
    username = input("Enter your username: ")
    request_chatrooms()
    chatroom = input("Type name of existing or new chatroom to connect to: ")

    get_messages_thread, send_message_thread, stop_event = start_all_threads(username, chatroom)

    try:
        get_messages_thread.join()
        print("STRANGE1")
        send_message_thread.join()
        print("STRANGE2")
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_event.set()
        get_messages_thread.join()
        send_message_thread.join()


if __name__ == "__main__":
    run_client()
