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

    # Test for item in order

    def test_read_an_orderitem(self):
        """It should Read an Order Items and assert that it exists"""
        orderitem = OrderItemsFactory()
        orderitem.create()
        orderitem_id = orderitem.id
        order_id = orderitem.order_id

        resp = self.client.get(f"/orders/{order_id}/items/{orderitem_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], orderitem_id)

    def test_read_an_orderitem_nonexistent_order(self):
        """It should not Read an Order Items for a non-existent order"""
        orderitem = OrderItemsFactory()
        orderitem.create()
        orderitem_id = orderitem.id

        resp = self.client.get("/orders/999/items/" + str(orderitem_id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_an_orderitem_nonexistent_orderitem(self):
        """It should not Read an Order Items for a non-existent orderitem"""
        orderitem = OrderItemsFactory()
        orderitem.create()
        order_id = orderitem.order_id

        resp = self.client.get("/orders/" + str(order_id) + "/items/999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

    # Test Create an item in an order
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

    # test read an order
    def test_get_order(self):
        """It should Get a single Order"""
        # get the id of a order
        test_order = self._create_orders(1)[0]
        response = self.client.get(f"/orders/{test_order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["order_status"], test_order.order_status)

    def test_get_order_not_found(self):
        """It should not Get a Order thats not found"""
        response = self.client.get("/orders/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # List an order -- Matt #

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
        response = self.client.get(BASE_URL + "?customer=" + str(customer_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 1)

    # Test update an order
    def test_update_order(self):
        """It should Update an existing Order"""
        # create a order to update
        test_order = OrderFactory()
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = response.get_json()
        logging.debug(new_order)
        new_order["order_status"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_order['id']}", json=new_order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_order = response.get_json()
        self.assertEqual(updated_order["order_status"], "unknown")

    # Test delete an item in an order
    def test_delete_an_orderitem(self):
        """It should Delete an Order Items and assert that it no longer exists"""
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

        resp = self.client.delete(f"/orders/{order_id}/items/{new_orderitem.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_an_orderitem_nonexistent_order(self):
        """It should not Delete an Order Items for a non-existent order"""
        resp = self.client.delete("/orders/999/items/999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_an_orderitem_nonexistent_orderitem(self):
        """It should not Delete an Order Items for a non-existent orderitem"""

        # Create an order using the factory
        order = OrderFactory()
        order.create()
        # Get the order id
        order_id = order.id

        resp = self.client.delete("/orders/" + str(order_id) + "/items/999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # Test delete an order
    def test_delete_an_order(self):
        """It should Delete an Order"""
        order = {"order_status": "pending", "customer_id": 1}
        resp = self.client.post("/orders", json=order)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["id"]
        resp = self.client.delete(f"/orders/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        new_order = Order.find(order_id)
        self.assertIsNone(new_order)

    def test_delete_an_nonexistent_order(self):
        """It should not Delete an Order that does not exist"""
        resp = self.client.delete("/orders/999")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    # Test Update Item Within an Order
    def test_update_item(self):
        """It should Update an item on an order"""
        # create a known order
        order = {
            "order_status": "pending",
            "customer_id": 1,
        }
        resp = self.client.post("/orders", json=order)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["id"]

        # create an order item
        orderitem = {
            "order_id": order_id,
            "product_id": 1,
            "price": 200,
            "quantity": 1,
        }
        resp = self.client.post(f"/orders/{order_id}/items", json=orderitem)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the created item details
        data = resp.get_json()
        logging.debug(data)
        item_id = data["id"]
        order_id = data["order_id"]
        data = {
            "order_id": order_id,
            "product_id": 1,
            "price": 1,
            "quantity": 201,
        }

        # send the update back
        resp = self.client.put(
            f"/orders/{order_id}/items/{item_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"/orders/{order_id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order_id)
        self.assertEqual(data["product_id"], 1)
        self.assertEqual(data["quantity"], 201)
        self.assertEqual(data["price"], 1)

        # code juan, test list items order

    def test_get_all_orders(self):
        """Test retrieving all orders without filters"""
        self._create_orders(2)
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_filter_orders_by_customer(self):
        """Test filtering orders by customer ID"""
        order1 = {"customer_id": 101, "order_status": "pending", "orderitems": []}
        order2 = {"customer_id": 202, "order_status": "shipped", "orderitems": []}
        self.client.post("/orders", json=order1)
        self.client.post("/orders", json=order2)

        response = self.client.get("/orders?customer=101")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertTrue(all(o["customer_id"] == 101 for o in results))

    def test_filter_orders_by_status(self):
        """Test filtering orders by status"""
        order1 = {"customer_id": 1, "order_status": "pending", "orderitems": []}
        order2 = {"customer_id": 1, "order_status": "delivered", "orderitems": []}
        self.client.post("/orders", json=order1)
        self.client.post("/orders", json=order2)

        response = self.client.get("/orders?order_status=delivered")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertTrue(all(o["order_status"] == "delivered" for o in results))

    def test_filter_orders_by_date(self):
        """Test filtering orders by creation date"""
        import time
        from datetime import datetime

        order1 = {"customer_id": 1, "order_status": "pending", "orderitems": []}
        self.client.post("/orders", json=order1)
        time.sleep(1)
        order2 = {"customer_id": 1, "order_status": "pending", "orderitems": []}
        self.client.post("/orders", json=order2)

        today = datetime.now().strftime("%Y-%m-%d")
        response = self.client.get(f"/orders?order_created={today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.get_json()
        self.assertTrue(isinstance(results, list))

    def test_invalid_customer_filter(self):
        """Test passing non-integer as customer filter"""
        response = self.client.get("/orders?customer=abc")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_date_filter(self):
        """Test passing invalid date string"""
        response = self.client.get("/orders?order_created=bad-date")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
