######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestYourResourceModel API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order, OrderItems
from tests.factories import OrderFactory, OrderItemsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Test create an order
    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        order = {"order_status": "pending", "customer_id": 1}
        # print("order: ", order)
        resp = self.client.post("/orders", json=order)
        print("resp: ", resp.json)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_order = Order.find(resp.json["id"])
        self.assertIsNotNone(new_order)
        self.assertEqual(new_order.order_status, "pending")

    def test_create_an_orderitem(self):
        """It should Create an Order Items and assert that it exists"""
        order = {
            "order_status": "pending",
            "customer_id": 1,
        }
        resp = self.client.post("/orders", json=order)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["id"]

        orderitem = {
            "order_id": order_id,
            "product_id": 1,
            "price": 200,
            "quantity": 1,
        }
        resp = self.client.post(f"/orders/{order_id}/items", json=orderitem)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_orderitem = OrderItems.find(resp.json["id"])
        self.assertIsNotNone(new_orderitem)
        self.assertEqual(new_orderitem.price, 200)

        new_order = Order.find(order_id)
        self.assertIsNotNone(new_order)
        self.assertEqual(new_order.orderitems[0].price, 200)

        self.assertEqual(len(new_order.orderitems), 1)

        orderitem = {
            "order_id": order_id,
            "product_id": 1,
            "price": 200,
            "quantity": 1,
        }
        resp = self.client.post(f"/orders/{order_id}/items", json=orderitem)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = Order.find(order_id)
        self.assertIsNotNone(new_order)
        self.assertEqual(len(new_order.orderitems), 2)

        self.assertEqual(new_order.orderitems[1].price, 200)

    def test_create_an_orderitem_nonexistent_order(self):
        """It should not Create an Order Items for a non-existent order"""
        orderitem = {
            "product_id": 1,
            "price": 200,
            "quantity": 1,
        }
        resp = self.client.post("/orders/999/items", json=orderitem)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
