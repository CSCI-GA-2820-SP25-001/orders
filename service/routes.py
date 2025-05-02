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
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from service.models import OrderItems, Order
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK ENDPOINT
######################################################################
@app.route("/health")
def health():
    """Health Check endpoint for Kubernetes probes"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Read an order item
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_orderitem(order_id, item_id):
    """
    Retrieve a single Order Item

    This endpoint will return an Order Item based on it's id
    """
    app.logger.info("Request to Retrieve an order item with id [%s]", item_id)

    # Attempt to find the Order Item and abort if not found
    orderitem = OrderItems.find(item_id)
    if not orderitem:
        abort(
            status.HTTP_404_NOT_FOUND, f"Order Item with id '{item_id}' was not found."
        )

    # Check if order_id exists if not exists, raise exception
    order = Order.find(order_id)
    if order is None:
        abort(status.HTTP_404_NOT_FOUND)

    # Check if the order_id in the path is the same as the order_id in the json
    if orderitem.order_id != order_id:
        app.logger.error(
            "Path order_id: %s does not match json order_id: %s",
            order_id,
            orderitem.order_id,
        )
        print(
            "Path order_id: %s does not match json order_id: %s",
            order_id,
            orderitem.order_id,
        )
        abort(status.HTTP_400_BAD_REQUEST)

    app.logger.info("Returning order item: %s", item_id)
    return jsonify(orderitem.serialize()), status.HTTP_200_OK


# CREATE AN ORDER
@app.route("/orders", methods=["POST"])
def create_order():
    """
    Create an Order

    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")
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
    """
    Create an Order Item

    This endpoint will create an Order Item based the data in the body that is posted
    """
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


# Read an order
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order

    This endpoint will return an Order based on it's id
    """
    app.logger.info("Request to Retrieve an order with id [%s]", order_id)

    # Attempt to find the Order and abort if not found
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    app.logger.info("Returning order: %s", order_id)
    return jsonify(order.serialize()), status.HTTP_200_OK


# GET A LIST OF ORDERS
@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request for order list")

    orders = []
    valid_filters = ["customer", "status", "date"]

    # Check for invalid query parameters
    for param in request.args:
        if param not in valid_filters:
            app.logger.error("Invalid filter parameter: %s", param)
            return (
                jsonify(
                    status=status.HTTP_400_BAD_REQUEST,
                    error="Bad Request",
                    message=f"Invalid filter parameter: {param}. Valid filters are: {', '.join(valid_filters)}",
                ),
                status.HTTP_400_BAD_REQUEST,
            )

    # Parse arguments from the query string
    customer_id = request.args.get("customer")
    order_status = request.args.get("status")
    order_date = request.args.get("date")
    # Apply filters based on query parameters
    if customer_id:
        app.logger.info("Find by customer: %s", customer_id)
        orders = Order.find_by_customer(customer_id)
    elif order_status:
        app.logger.info("Find by status: %s", order_status)
        orders = Order.find_by_status(order_status)
    elif order_date:
        app.logger.info("Find by date: %s", order_date)
        try:
            # Validate date format (YYYY-MM-DD)
            datetime.datetime.strptime(order_date, "%Y-%m-%d")
            orders = Order.find_by_date(order_date)
        except ValueError:
            app.logger.error("Invalid date format: %s", order_date)
            return (
                jsonify(
                    status=status.HTTP_400_BAD_REQUEST,
                    error="Bad Request",
                    message="Invalid date format. Date must be in YYYY-MM-DD format.",
                ),
                status.HTTP_400_BAD_REQUEST,
            )
    else:
        app.logger.info("Find all")
        orders = Order.all()

    results = [order.serialize() for order in orders]
    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


# DELETE AN ORDER ITEM
@app.route("/orders/<int:order_id>/items/<int:product_id>", methods=["DELETE"])
def delete_orderitem(order_id, product_id):
    """
    Delete an Order Item

    This endpoint will delete an Order Item based the id specified in the path

    Args:
        order_id (int): the id of the order to delete
        product_id (int): the id of the order item to delete

    Returns:
        status: 204 No Content
    """
    app.logger.info("Request to delete an Order Item")

    # Check if order_id exists if not exists, return 204
    order = Order.find(order_id)
    if order is None:
        return {}, status.HTTP_204_NO_CONTENT

    # Check if orderproduct_id exists if not exists, return 204
    orderitem = OrderItems.find(product_id)
    if orderitem is None:
        return {}, status.HTTP_204_NO_CONTENT

    # Delete the Order Item
    orderitem.delete()
    return {}, status.HTTP_204_NO_CONTENT


# DELETE AN ORDER
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based the id specified in the path

    Args:
        order_id (int): the id of the order to delete

    Returns:
        status: HTTP_204_NO_CONTENT
    """
    app.logger.info("Request to delete an Order")
    order = Order.find(order_id)
    if order is None:
        return "", status.HTTP_204_NO_CONTENT
    order.delete()
    return {}, status.HTTP_204_NO_CONTENT


# Update an order -- Juan #


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order

    This endpoint will update an Order based the body that is posted
    """
    app.logger.info("Request to Update an order with id [%s]", order_id)
    check_content_type("application/json")

    # Attempt to find the Order and abort if not found
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Update the Order with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)

    # Ensure all required fields are present
    # If order_created is not in the request data, use the existing value or set a default
    if "order_created" not in data:
        if order.order_created:
            data["order_created"] = order.order_created.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            # If order_created is None, set it to the current time
            data["order_created"] = datetime.datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

    # If order_updated is not in the request data, set it to the current time
    if "order_updated" not in data:
        data["order_updated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # If orderitems is not in the request data, use the existing items
    if "orderitems" not in data:
        data["orderitems"] = []

    # Log the complete data being processed
    app.logger.info("Complete data for deserialize: %s", data)

    order.deserialize(data)

    # Save the updates to the database
    order.update()

    app.logger.info("Order with ID: %d updated.", order.id)
    return jsonify(order.serialize()), status.HTTP_200_OK


# UPDATE AN ITEM IN AN ORDER
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_items(order_id, item_id):
    """
    Update an Item

    This endpoint will update an Item based the body that is posted
    """
    app.logger.info("Request to update Item %s for Order id: %s", item_id, order_id)
    check_content_type("application/json")

    # See if the item exists and abort if it doesn't
    orderitem = OrderItems.find(item_id)
    if not orderitem:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item with id '{item_id}' could not be found.",
        )

    # Check if the order exists
    order = Order.find(order_id)
    if not order:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{order_id}' could not be found.",
        )

    # Check if the order_id in the path matches the order_id of the item
    if orderitem.order_id != order_id:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Item with id '{item_id}' does not belong to order with id '{order_id}'.",
        )

    # Get the request data
    data = request.get_json()

    # Validate quantity
    if "quantity" in data:
        quantity = data.get("quantity")

        # Check if quantity is a positive integer
        if not isinstance(quantity, int) or quantity <= 0:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Quantity must be a positive integer.",
            )

    # Update from the json in the body of the request
    orderitem.deserialize(request.get_json())
    orderitem.update()

    # Update the order's updated timestamp
    order.order_updated = datetime.datetime.now()
    order.update()

    return jsonify(orderitem.serialize()), status.HTTP_200_OK


# GET A LIST OF ORDER ITEMS
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_orderitems(order_id):
    """
    Retrieve a list of Order Items for a given order

    This endpoint will return all items associated with a specific order
    identified by the order_id in the URL path. If the order does not exist,
    a status of 204 (No Content) will be returned.
    """

    app.logger.info("Request for order item list")
    order = Order.find(order_id)
    if order is None:
        return "", status.HTTP_204_NO_CONTENT
    orderitems = OrderItems.find_by_order_id(order_id)
    results = [orderitem.serialize() for orderitem in orderitems]
    app.logger.info("Returning %d order items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# CANCEL AN ORDER
######################################################################


@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """Cancelling a Order makes it unavailable"""
    app.logger.info("Request to Cancel order with id: %d", order_id)

    # Attempt to find the Order and abort if not found
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # you can only cancel orders that are pending
    if order.order_status.lower() != "pending":
        abort(
            status.HTTP_409_CONFLICT,
            f"Order with id '{order_id}' cannot be canceled because it is in '{order.order_status}' status.",
        )

    # update status to canceled
    order.order_status = "canceled"
    order.order_updated = datetime.datetime.now()
    order.update()

    app.logger.info("Order with ID: %d has been canceled.", order_id)
    return jsonify(order.serialize()), status.HTTP_200_OK
