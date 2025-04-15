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
# cspell:ignore userid
# pylint: disable=duplicate-code

"""
Test cases for Order Model
"""

import logging
import os
import datetime
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from wsgi import app
from service.models import Order, OrderItems, DataValidationError, db
from tests.factories import OrderFactory, OrderItemsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        ORDER   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(TestCase):
    """Order Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(OrderItems).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            customer_id=fake_order.customer_id,
            order_status=fake_order.order_status,
            order_created=fake_order.order_created,
            order_updated=fake_order.order_updated,
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_id, fake_order.customer_id)
        self.assertEqual(order.order_status, fake_order.order_status)
        self.assertEqual(order.order_created, fake_order.order_created)
        self.assertEqual(order.order_updated, fake_order.order_updated)

    def test_add_an_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    @patch("service.models.db.session.commit")
    def test_add_order_failed(self, exception_mock):
        """It should not create an Order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.create)

    def test_read_order(self):
        """It should Read an order"""
        order = OrderFactory()
        order.create()

        # Read it back
        found_order = Order.find(order.id)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.customer_id, order.customer_id)
        self.assertEqual(found_order.order_status, order.order_status)
        self.assertEqual(found_order.order_created, order.order_created)
        self.assertEqual(found_order.order_updated, order.order_updated)

    def test_update_order(self):
        """It should Update an order"""
        order = OrderFactory(order_status="Brand New Status")
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        self.assertEqual(order.order_status, "Brand New Status")

        # Fetch it back
        order = Order.find(order.id)
        order.order_status = "Another Status"
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(order.order_status, "Another Status")

    @patch("service.models.db.session.commit")
    def test_update_order_failed(self, exception_mock):
        """It should not update an Order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.update)

    def test_delete_an_order(self):
        """It should Delete an order from the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.delete()
        orders = order.all()
        self.assertEqual(len(orders), 0)

    @patch("service.models.db.session.commit")
    def test_delete_order_failed(self, exception_mock):
        """It should not delete an order on database error"""
        exception_mock.side_effect = Exception()
        order = OrderFactory()
        self.assertRaises(DataValidationError, order.delete)

    def test_list_all_orders(self):
        """It should List all orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(5):
            order.create()
        # Assert that there are not 5 orders in the database
        orders = Order.all()
        self.assertEqual(len(orders), 5)

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        orderitem = OrderItemsFactory(order=order)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["customer_id"], order.customer_id)
        self.assertEqual(serial_order["order_status"], order.order_status)
        self.assertEqual(serial_order["order_created"], order.order_created)
        self.assertEqual(serial_order["order_updated"], order.order_updated)
        self.assertEqual(len(serial_order["orderitems"]), 1)
        self.assertEqual(serial_order["orderitems"][0]["id"], orderitem.id)
        self.assertEqual(serial_order["orderitems"][0]["order_id"], orderitem.order_id)
        self.assertEqual(
            serial_order["orderitems"][0]["product_id"], orderitem.product_id
        )
        self.assertEqual(serial_order["orderitems"][0]["price"], orderitem.price)
        self.assertEqual(serial_order["orderitems"][0]["quantity"], orderitem.quantity)

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        OrderItemsFactory(order=order)
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.order_status, order.order_status)
        self.assertEqual(new_order.order_created, order.order_created)
        self.assertEqual(new_order.order_updated, order.order_updated)
        self.assertEqual(len(new_order.orderitems), 1)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_orderitem_key_error(self):
        """It should not Deserialize an order item with a KeyError"""
        orderitem = OrderItems()
        self.assertRaises(DataValidationError, orderitem.deserialize, {})

    def test_deserialize_orderitem_type_error(self):
        """It should not Deserialize an order item with a TypeError"""
        orderitem = OrderItems()
        self.assertRaises(DataValidationError, orderitem.deserialize, [])

    def test_find_by_customer(self):
        """It should Find Orders by Customer ID"""
        # Create 5 orders with different customer IDs
        orders = []
        for i in range(5):
            customer_id = i + 100
            orders.append(OrderFactory(customer_id=customer_id))
            orders[i].create()

        # Create 2 more orders with the same customer ID
        same_customer_id = 999
        for _ in range(2):
            order = OrderFactory(customer_id=same_customer_id)
            order.create()
            orders.append(order)

        # Test finding orders by customer ID
        found_orders = Order.find_by_customer(same_customer_id)
        self.assertEqual(len(found_orders), 2)
        for order in found_orders:
            self.assertEqual(order.customer_id, same_customer_id)

        # Test finding orders by customer ID as string
        found_orders = Order.find_by_customer(str(same_customer_id))
        self.assertEqual(len(found_orders), 2)
        for order in found_orders:
            self.assertEqual(order.customer_id, same_customer_id)

        # Test with invalid customer ID
        found_orders = Order.find_by_customer("invalid")
        self.assertEqual(len(found_orders), 0)

    def test_find_by_status(self):
        """It should Find Orders by Status"""
        # Create 5 orders with different statuses
        orders = []
        for i, status in enumerate(
            ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
        ):
            orders.append(OrderFactory(order_status=status))
            orders[i].create()

        # Create 2 more orders with the same status
        same_status = "PROCESSING"
        for _ in range(2):
            order = OrderFactory(order_status=same_status)
            order.create()
            orders.append(order)

        # Test finding orders by status
        found_orders = Order.find_by_status(same_status)
        self.assertEqual(len(found_orders), 2)
        for order in found_orders:
            self.assertEqual(order.order_status, same_status)

    def test_find_by_date(self):
        """It should Find Orders by Date"""
        # Create orders with specific dates
        date1 = datetime.datetime(2023, 1, 15)
        date2 = datetime.datetime(2023, 2, 20)

        # Create 2 orders with the first date
        for _ in range(2):
            order = OrderFactory(order_created=date1)
            order.create()

        # Create 3 orders with the second date
        for _ in range(3):
            order = OrderFactory(order_created=date2)
            order.create()

        # Test finding orders by the first date
        found_orders = Order.find_by_date("2023-01-15")
        self.assertEqual(len(found_orders), 2)

        # Test finding orders by the second date
        found_orders = Order.find_by_date("2023-02-20")
        self.assertEqual(len(found_orders), 3)

        # Test with invalid date format
        found_orders = Order.find_by_date("invalid-date")
        self.assertEqual(len(found_orders), 0)

        # Test with database error
        with patch("service.models.order.db.func.date") as mock_date:
            mock_date.side_effect = SQLAlchemyError("Database error")
            found_orders = Order.find_by_date("2023-01-15")
            self.assertEqual(len(found_orders), 0)
