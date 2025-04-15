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
Order Steps

Steps file for Order.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given, when, then  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400

WAIT_TIMEOUT = 60


@given("the following orders")
def step_impl(context):
    """Delete all Orders and load new ones"""

    # Get a list all of the orders
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for order in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{order['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new orders
    for row in context.table:
        payload = {
            "customer_id": row["customer_id"],
            "order_status": row["order_status"],
            "order_created": row["order_created"],
            "order_updated": row["order_updated"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


# Order History API Tests

@when('I request orders for customer with id "{customer_id}"')
def step_impl(context, customer_id):
    """Make a request to list orders for a specific customer"""
    rest_endpoint = f"{context.base_url}/orders?customer={customer_id}"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    context.customer_id = customer_id


@when('I request orders with an invalid filter parameter')
def step_impl(context):
    """Make a request with an invalid filter parameter"""
    rest_endpoint = f"{context.base_url}/orders?invalid=value"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)


@then('I should receive a list of {count:d} order')
def step_impl(context, count):
    """Check that the response contains the expected number of orders"""
    if context.resp.status_code == HTTP_204_NO_CONTENT:
        orders = []
    else:
        orders = context.resp.json()
    expect(len(orders)).equal_to(count)


@then('I should receive a list of {count:d} orders')
def step_impl(context, count):
    """Check that the response contains the expected number of orders"""
    if context.resp.status_code == HTTP_204_NO_CONTENT:
        orders = []
    else:
        orders = context.resp.json()
    expect(len(orders)).equal_to(count)


@then('the orders should have the following statuses')
def step_impl(context):
    """Check that the orders have the expected statuses"""
    orders = context.resp.json()
    
    # Convert the table to a list of statuses for easier comparison
    expected_statuses = []
    for row in context.table:
        expected_statuses.append(row["order_status"])
    
    # Check that each order has one of the expected statuses
    for order in orders:
        expect(order["order_status"] in expected_statuses).equal_to(True)



@then('the response should contain an error message about invalid filter')
def step_impl(context):
    """Check that the response contains an error message about an invalid filter parameter"""
    response_json = context.resp.json()
    expect("message" in response_json).equal_to(True)
    expect("Invalid filter parameter" in response_json["message"]).equal_to(True)
