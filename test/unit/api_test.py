import unittest
import http.client
from app import api


class TestApiEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = api.api_application.test_client()

    def test_hello_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response.data.decode(), "Hello from The Calculator!\n")

    def test_add_endpoint_valid_numbers(self):
        response = self.client.get("/calc/add/2/3")
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response.data.decode(), "5")

        response = self.client.get("/calc/add/2.5/3.5")
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response.data.decode(), "6.0")

    def test_add_endpoint_invalid_numbers(self):
        response = self.client.get("/calc/add/a/3")
        self.assertEqual(response.status_code, http.client.BAD_REQUEST)
        self.assertIn("Operator cannot be converted to number", response.data.decode())

        response = self.client.get("/calc/add/2/b")
        self.assertEqual(response.status_code, http.client.BAD_REQUEST)
        self.assertIn("Operator cannot be converted to number", response.data.decode())

    def test_substract_endpoint_valid_numbers(self):
        response = self.client.get("/calc/substract/5/3")
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response.data.decode(), "2")

        response = self.client.get("/calc/substract/5.5/2.5")
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response.data.decode(), "3.0")

    def test_substract_endpoint_invalid_numbers(self):
        response = self.client.get("/calc/substract/x/3")
        self.assertEqual(response.status_code, http.client.BAD_REQUEST)
        self.assertIn("Operator cannot be converted to number", response.data.decode())

        response = self.client.get("/calc/substract/5/y")
        self.assertEqual(response.status_code, http.client.BAD_REQUEST)
        self.assertIn("Operator cannot be converted to number", response.data.decode())


if __name__ == "__main__":
    unittest.main()