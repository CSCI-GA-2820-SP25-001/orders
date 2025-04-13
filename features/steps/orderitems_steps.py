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
Order Items Steps

Steps file for OrderItems.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import requests
from compare3 import expect
from behave import given, when, then  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following order items")
def step_impl(context):
    """Create order items for testing"""
    # First get all orders to find their IDs
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    orders = context.resp.json()

    # Create a mapping of customer_id to order_id
    order_map = {}
    for order in orders:
        order_map[order["customer_id"]] = order["id"]

    # Create the order items
    for row in context.table:
        order_id = int(row["order_id"])
        # Find the actual order ID from the database
        actual_order_id = None
        for order in orders:
            if order["id"] == order_id:
                actual_order_id = order_id
                break

        if actual_order_id is None:
            continue  # Skip if order doesn't exist

        payload = {
            "order_id": actual_order_id,
            "product_id": int(row["product_id"]),
            "quantity": int(row["quantity"]),
            "price": float(row["price"]),
        }

        item_endpoint = f"{context.base_url}/orders/{actual_order_id}/items"
        context.resp = requests.post(item_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@when('I request to list items for order with id "{order_id}"')
def step_impl(context, order_id):
    """Make a request to list items for a specific order"""
    rest_endpoint = f"{context.base_url}/orders/{order_id}/items"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    context.order_id = order_id


@then("I should receive a list of {count:d} order items")
def step_impl(context, count):
    """Check that the response contains the expected number of items"""
    if context.resp.status_code == HTTP_204_NO_CONTENT:
        items = []
    else:
        items = context.resp.json()
    expect(len(items)).equal_to(count)


@then('the response status code should be "{status_code}"')
def step_impl(context, status_code):
    """Check that the response has the expected status code"""
    expect(context.resp.status_code).equal_to(int(status_code))


@then("the response should include the following items")
def step_impl(context):
    """Check that the response includes the expected items"""
    items = context.resp.json()

    # Convert the table to a list of dictionaries for easier comparison
    expected_items = []
    for row in context.table:
        expected_item = {
            "product_id": int(row["product_id"]),
            "quantity": int(row["quantity"]),
            "price": float(row["price"]),
        }
        expected_items.append(expected_item)

    # Check that each expected item is in the response
    for expected_item in expected_items:
        found = False
        for item in items:
            if (
                item["product_id"] == expected_item["product_id"]
                and item["quantity"] == expected_item["quantity"]
                and item["price"] == expected_item["price"]
            ):
                found = True
                break
        expect(found).equal_to(True)


@then("I should receive an empty response")
def step_impl(context):
    """Check that the response is empty"""
    expect(context.resp.text).equal_to("")


@then("I should receive an empty list")
def step_impl(context):
    """Check that the response is an empty list"""
    if context.resp.status_code == HTTP_204_NO_CONTENT:
        items = []
    else:
        items = context.resp.json()
    expect(len(items)).equal_to(0)
