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
from service.routes import jsonify, request, url_for, abort
from service.common import status
from service.models import db, Order, OrderItems
from tests.factories import OrderFactory, OrderItemsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/orders"


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

    ############################################################
    # Utility function to bulk create orders
    ############################################################

    def _create_orders(self, count: int = 1) -> list:
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            test_orders = OrderFactory()
            response = self.client.post(BASE_URL, json=test_orders.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test order",
            )
            new_order = response.get_json()
            test_orders.id = new_order["id"]
            orders.append(test_orders)
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    # Test update root url
    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Orders and Order Items REST API Service")

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

    ### List an order -- Matt ###

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order_list_by_customer_id(self):
        """It should Get a list of Orders by customer_id"""
        orders = self._create_orders(5)
        customer_id = orders[0].customer_id
        response = self.client.get(BASE_URL + "?customer_id=" + str(customer_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)
