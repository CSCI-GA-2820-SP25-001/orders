"""
Test cases for the Error Handlers
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order, OrderItems
from service.common.error_handlers import internal_server_error

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class ErrorHandlerService(TestCase):
    """Error Handlers Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(OrderItems).delete()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_405_error(self):
        """Test 405 error"""
        response = self.client.patch(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_400_error(self):
        """Test 400 error"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_internal_server_error(self):
        """It should return 500 internal server error"""
        # Create a mock Flask response
        mock_error = Exception("Test internal server error")

        # Call the error handler directly
        response, status_code = internal_server_error(mock_error)

        # Check the response
        self.assertEqual(status_code, 500)
        data = response.get_json()
        self.assertEqual(data["status"], 500)
        self.assertEqual(data["error"], "Internal Server Error")
        self.assertIn("Test internal server error", data["message"])
