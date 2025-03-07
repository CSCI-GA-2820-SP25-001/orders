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
# pylint: disable=duplicate-code

"""
Test cases for Order Items Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, OrderItems, db, DataValidationError
from tests.factories import OrderFactory, OrderItemsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        ORDER ITEM   M O D E L   T E S T   C A S E S
######################################################################
class TestOrderItem(TestCase):
    """Order Item Model Test Cases"""

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

    def test_add_order_orderitem(self):
        """It should Create an order with an orderitem and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        orderitem = OrderItemsFactory(order=order)
        order.orderitems.append(orderitem)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.orderitems[0].price, orderitem.price)

        orderitem2 = OrderItemsFactory(order=order)
        order.orderitems.append(orderitem2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.orderitems), 2)
        self.assertEqual(new_order.orderitems[1].price, orderitem2.price)

    @patch("service.models.db.session.commit")
    def test_add_orderitem_failed(self, exception_mock):
        """It should not create an Order Item on database error"""
        exception_mock.side_effect = Exception()
        orderitem = OrderItemsFactory()
        self.assertRaises(DataValidationError, orderitem.create)

    def test_update_order_orderitem(self):
        """It should Update an orders orderitem"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        orderitem = OrderItemsFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        old_orderitem = order.orderitems[0]
        print("%r", old_orderitem)
        self.assertEqual(old_orderitem.quantity, orderitem.quantity)
        # Change the quantity
        old_orderitem.quantity = 6
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        orderitem = order.orderitems[0]
        self.assertEqual(orderitem.quantity, 6)

    @patch("service.models.db.session.commit")
    def test_update_orderitem_failed(self, exception_mock):
        """It should not update an Order Item on database error"""
        exception_mock.side_effect = Exception()
        orderitem = OrderItemsFactory()
        self.assertRaises(DataValidationError, orderitem.update)

    def test_delete_order_orderitem(self):
        """It should Delete an orders orderitem"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        orderitem = OrderItemsFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        orderitem = order.orderitems[0]
        orderitem.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.orderitems), 0)

    @patch("service.models.db.session.commit")
    def test_delete_orderitem_failed(self, exception_mock):
        """It should not delete an order item on database error"""
        exception_mock.side_effect = Exception()
        orderitem = OrderItemsFactory()
        self.assertRaises(DataValidationError, orderitem.delete)

    def test_serialize_an_orderitem(self):
        """It should serialize an OrderItems"""
        orderitem = OrderItemsFactory()
        serial_orderitem = orderitem.serialize()
        self.assertEqual(serial_orderitem["id"], orderitem.id)
        self.assertEqual(serial_orderitem["order_id"], orderitem.order_id)
        self.assertEqual(serial_orderitem["product_id"], orderitem.product_id)
        self.assertEqual(serial_orderitem["quantity"], orderitem.quantity)
        self.assertEqual(serial_orderitem["price"], orderitem.price)

    def test_deserialize_an_orderitem(self):
        """It should deserialize an OrderItems"""
        orderitem = OrderItemsFactory()
        orderitem.create()
        new_orderitem = OrderItems()
        new_orderitem.deserialize(orderitem.serialize())
        self.assertEqual(new_orderitem.order_id, orderitem.order_id)
        self.assertEqual(new_orderitem.product_id, orderitem.product_id)
        self.assertEqual(new_orderitem.quantity, orderitem.quantity)
        self.assertEqual(new_orderitem.price, orderitem.price)

    def test_deserialize_an_orderitem_with_key_error(self):
        """It should not deserialize an OrderItems with key error"""
        orderitem = OrderItemsFactory()
        orderitem.create()
        serial_orderitem = orderitem.serialize()
        del serial_orderitem["order_id"]
        new_orderitem = OrderItems()
        with self.assertRaises(DataValidationError):
            new_orderitem.deserialize(serial_orderitem)
