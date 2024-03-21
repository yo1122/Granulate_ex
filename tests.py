import unittest
from app import app
from constants import SUCCESS

SIMPLE_MESSAGE_DATA = {'message': 'Test message'}
SIMPLE_AUTH_DATA = {'Authorization': 'Basic dXNlcjE='}  # Base64 encoded "user1"


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
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


if __name__ == '__main__':
    unittest.main()
