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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""
import datetime
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import OrderItems, Order
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "WARNING: Return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# CREATE AN ORDER
@app.route("/orders", methods=["POST"])
def create_order():
    app.logger.info("Request to create an Order")
    order = Order()

    # Get the JSON from the request
    orderjson = request.get_json()
    # Set the created and updated time
    orderjson["order_created"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    orderjson["order_updated"] = orderjson["order_created"]
    # If orderitems is missing, set to empty array
    if "orderitems" not in orderjson:
        orderjson["orderitems"] = []

    # Deserialize the data into a model and create in database
    order.deserialize(orderjson)
    order.create()
    message = order.serialize()
    return message, status.HTTP_201_CREATED


# CREATE AN ORDER ITEM
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def create_orderitem(order_id):
    app.logger.info("Request to create an Order Item")

    # Check if order_id exists if not exists, raise exception
    order = Order.find(order_id)
    if order is None:
        abort(status.HTTP_404_NOT_FOUND)

    orderitem = OrderItems()

    # Get the JSON from the request
    orderitemjson = request.get_json()
    # Fill in the order_id
    orderitemjson["order_id"] = order_id

    # Deserialize the data into a model and create in database
    orderitem.deserialize(orderitemjson)
    orderitem.create()
    message = orderitem.serialize()
    return message, status.HTTP_201_CREATED
