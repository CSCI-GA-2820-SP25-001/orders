"""
Test cases for Health Check Endpoint
"""

import unittest
from wsgi import app
from service.common import status


class TestHealthCheck(unittest.TestCase):
    """Test cases for the Health Check Endpoint"""

    def setUp(self):
        """This runs before each test"""
        self.app = app.test_client()

    def test_health_endpoint(self):
        """It should return a 200 OK response with status OK"""
        resp = self.app.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")


if __name__ == "__main__":
    unittest.main()
