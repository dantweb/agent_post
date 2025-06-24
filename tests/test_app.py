import sys
import os
import unittest
import json

# Add the parent directory to the Python path to allow imports from `app.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app  # Import the Flask app instance


class TestMessageAPI(unittest.TestCase):
    def setUp(self):
        # Create a test client for the Flask app
        self.client = app.test_client()

    def test_post_message(self):
        # Test sending a POST request
        response = self.client.post(
            '/messages',
            data=json.dumps({"message": "Hello, World!"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)  # Check the status code
        self.assertIn("Message added successfully!", response.get_data(as_text=True))  # Check response text

    def test_get_messages(self):
        # Add a test message to the in-memory store with a POST request
        post_response = self.client.post(
            '/messages',
            data=json.dumps({"message": "Hello, Flask!"}),
            content_type='application/json'
        )
        self.assertEqual(post_response.status_code, 201)

        # Test GET request to retrieve all messages
        get_response = self.client.get('/messages')
        self.assertEqual(get_response.status_code, 200)  # Check that the status is OK

        # Check that the message appears in the response
        response_data = json.loads(get_response.data)
        self.assertIn("Hello, Flask!", response_data['messages'])


if __name__ == '__main__':
    unittest.main()
