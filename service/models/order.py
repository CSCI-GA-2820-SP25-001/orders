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
from datetime import date
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
    name = db.Column(db.String(64), nullable=False)
    userid = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.String(32), nullable=True)  # phone number is optional
    orderitems = db.relationship("OrderItems", backref="order", passive_deletes=True)

    def __repr__(self):
        return f"<Order {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Order into a dictionary"""
        order = {
            "id": self.id,
            "name": self.name,
            "userid": self.userid,
            "email": self.email,
            "phone_number": self.phone_number,
            "orderitems": [],
        }
        for item in self.orderitems:
            order["orderitems"].append(item.serialize())
        return order

    def deserialize(self, data):
        """
        Populates an Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.userid = data["userid"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
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
