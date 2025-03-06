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
from .persistent_base import db, PersistentBase, DataValidationError
from .orderitems import OrderItems

logger = logging.getLogger("flask.app")


######################################################################
#  ORDER   M O D E L
######################################################################
class Order(db.Model, PersistentBase):
    """
    Class that represents an Account
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
    def find_by_name(cls, name):
        """Returns all Orders with the given name

        Args:
            name (string): the name of the Orders you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
