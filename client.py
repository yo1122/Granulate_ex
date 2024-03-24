import os

import requests
import threading
import time

from constants import POLL_TIME, SERVER_HOST, SERVER_PORT

SERVER_URL = f"https://{os.environ.get(SERVER_HOST, '0.0.0.0')}:{os.environ.get(SERVER_PORT, 5000)}"


def run_client():
    username = input("Enter your username: ")
    stop_event = threading.Event()
    get_messages_thread = threading.Thread(target=get_messages, args=(stop_event,))
    send_message_thread = threading.Thread(target=send_message, args=(username, stop_event))
    get_messages_thread.start()
    send_message_thread.start()

    try:
        get_messages_thread.join()
        send_message_thread.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_event.set()
        get_messages_thread.join()
        send_message_thread.join()


def get_messages(stop_event):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #  WARNING: Verify false for debug only
    print("Messages:")
    while not stop_event.is_set():
        response = requests.get(f"{SERVER_URL}/get_messages", verify=False)
        if response.status_code == 200:
            messages = response.json()
            for message in messages:
                print(f"{message['username']}: {message['message']}")
        else:
            print("Failed to fetch messages.")
        time.sleep(POLL_TIME)


def send_message(username, stop_event):
    #  WARNING: Verify false for debug only

    while not stop_event.is_set():
        message = input("Enter your message: ")
        data = {"message": message}
        response = requests.post(f"{SERVER_URL}/send_message", json=data, auth=(username, ""), verify=False)
        if response.status_code == 201:
            print("Message sent successfully.")
            return True
        else:
            print("Failed to send message.")
            return False


if __name__ == "__main__":
    run_client()
