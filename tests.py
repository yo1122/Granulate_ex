import threading
import threading
import time
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

import client
from app import app
from constants import SUCCESS, POLL_TIME

SIMPLE_MESSAGE_DATA = {'message': 'Test message'}
SIMPLE_AUTH_DATA = {'Authorization': 'Basic dXNlcjE='}  # Base64 encoded "user1"


class TestServer(unittest.TestCase):
    def setUp(self):
        # Mock flask server
        self.app = app.test_client()

    def test_send_message_responding(self):
        response = self.app.post('/send_message', json=SIMPLE_MESSAGE_DATA, headers=SIMPLE_AUTH_DATA)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {SUCCESS: True})

    def test_get_messages_gets_sent_message(self):
        self.app.post('/send_message', json=SIMPLE_MESSAGE_DATA, headers=SIMPLE_AUTH_DATA)

        response = self.app.get('/get_messages')
        simple_return_data = SIMPLE_MESSAGE_DATA
        simple_return_data.update({"username": "user1"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(simple_return_data, response.json)


class TestClient(unittest.TestCase):

    @patch('client.requests.get')
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_messages_success(self, mock_stdout, mock_get):
        # Mock the response from the server
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"username": "user1", "message": "Hello"},
            {"username": "user2", "message": "Hi"}
        ]
        mock_get.return_value = mock_response
        stop_event = threading.Event()

        with patch('builtins.input', side_effect=['test_user', KeyboardInterrupt]):
            get_messages_thread = threading.Thread(target=client.get_messages, args=(stop_event,))
            get_messages_thread.start()
            time.sleep(POLL_TIME * 3)
            stop_event.set()
            get_messages_thread.join()

        # Capture the printed output
        printed_output = mock_stdout.getvalue().strip()

        self.assertIn("user1: Hello", printed_output)
        self.assertIn("user2: Hi", printed_output)

    @patch('client.requests.post')
    @patch('sys.stdout', new_callable=StringIO)
    def test_send_message_success(self, mock_stdout, mock_post):
        # Mock the response from the server
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        stop_event = threading.Event()

        with patch('builtins.input', side_effect=['Hello world', KeyboardInterrupt]):
            get_messages_thread = threading.Thread(target=client.send_message, args=('test_user', stop_event,))
            get_messages_thread.start()
            stop_event.set()
            get_messages_thread.join()

        # Capture the printed output
        printed_output = mock_stdout.getvalue().strip()

        self.assertIn("Message sent successfully.", printed_output)


if __name__ == '__main__':
    unittest.main()
