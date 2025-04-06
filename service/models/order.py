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
# cspell: ignore= userid, backref
"""
Persistent Base class for database CRUD functions
"""

import logging

# from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from .persistent_base import db, PersistentBase, DataValidationError
from .orderitems import OrderItems

logger = logging.getLogger("flask.app")


######################################################################
#  ORDER   M O D E L
######################################################################
class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(64), nullable=False)
    order_created = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )
    order_updated = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )
    orderitems = db.relationship("OrderItems", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order id={self.id}>"

    def serialize(self):
        """Converts an Order into a dictionary"""
        order = {
            "id": self.id,
            "customer_id": self.customer_id,
            "order_status": self.order_status,
            "order_created": self.order_created,
            "order_updated": self.order_updated,
            "orderitems": [],
        }
        for item in self.orderitems:
            order["orderitems"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Populates an Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.order_status = data["order_status"]
            self.order_created = data["order_created"]
            self.order_updated = data["order_updated"]
            # handle inner list of items
            item_list = data.get("orderitems")
            for json_item in item_list:
                item = OrderItems()
                item.deserialize(json_item)
                self.orderitems.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data " + str(error)
            ) from error

        return self

    @classmethod
    def find_by_customer(cls, customer_id):
        """Returns all orders from the database with the given customer_id

        Args:
            customer_id (int): the customer_id of the orders to find

        Returns:
            a list of Order objects. Could be empty.
        """
        try:
            # Convert string to int if it's a string
            if isinstance(customer_id, str):
                customer_id = int(customer_id)
            return cls.query.filter(cls.customer_id == customer_id).all()
        except (ValueError, TypeError):
            # Return empty list if conversion fails
            return []

    @classmethod
    def find_by_status(cls, status):
        """Returns all orders from the database with the given status
        Args:
            status (string): the status of the orders to find
        Returns:
            a list of Order objects. Could be empty.
        """
        return cls.query.filter(cls.order_status == status).all()

    @classmethod
    def find_by_date(cls, date_str):
        """Returns all orders from the database created on the given date
        Args:
            date_str (string): the date of the orders to find in format YYYY-MM-DD
        Returns:
            a list of Order objects. Could be empty.
        """
        try:
            # Use SQLAlchemy's cast function to convert the date string to a date
            # and compare with the date part of order_created
            return cls.query.filter(
                db.func.date(cls.order_created) == db.func.cast(date_str, db.Date)
            ).all()
        except (ValueError, TypeError):
            # Return empty list if there's an error with the date format
            return []
        except SQLAlchemyError:
            # Return empty list if there's a database error
            logger.error("Database error occurred when finding orders by date")
            return []
