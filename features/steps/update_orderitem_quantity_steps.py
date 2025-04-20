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
Update Order Item Quantity Steps

Steps file for update_orderitem_quantity.feature
"""
# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import json
import requests
from behave import when, then  # pylint: disable=no-name-in-module
from compare3 import expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404

WAIT_TIMEOUT = 60


@when(
    'I update the quantity of product "{product_id}" in order "{order_id}" to "{quantity}"'
)
def step_impl(context, product_id, order_id, quantity):
    """Update the quantity of a product in an order"""
    # First, get the order items to find the item ID
    rest_endpoint = f"{context.base_url}/orders/{order_id}/items"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)

    if context.resp.status_code == HTTP_200_OK:
        items = context.resp.json()
        item_id = None

        # Find the item with the matching product_id
        for item in items:
            if str(item["product_id"]) == product_id:
                item_id = item["id"]
                break

        if item_id:
            # Update the item quantity
            update_endpoint = f"{context.base_url}/orders/{order_id}/items/{item_id}"
            data = {
                "order_id": int(order_id),
                "product_id": int(product_id),
                "quantity": int(quantity),
                "price": item["price"],  # Keep the original price
            }

            context.resp = requests.put(
                update_endpoint, json=data, timeout=WAIT_TIMEOUT
            )
        else:
            # If item not found, create a fake response with 404
            context.resp = type(
                "obj",
                (object,),
                {
                    "status_code": HTTP_404_NOT_FOUND,
                    "text": json.dumps(
                        {
                            "message": f"Item with product_id '{product_id}' not found in order '{order_id}'"
                        }
                    ),
                    "json": lambda: {
                        "message": f"Item with product_id '{product_id}' not found in order '{order_id}'"
                    },
                },
            )

    # Store the order_id and product_id for later steps
    context.order_id = order_id
    context.product_id = product_id


@then('the order item should have a quantity of "{quantity}"')
def step_impl(context, quantity):
    """Check that the order item has the expected quantity"""
    # Get the updated item
    rest_endpoint = f"{context.base_url}/orders/{context.order_id}/items"
    resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)

    expect(resp.status_code).equal_to(HTTP_200_OK)

    items = resp.json()
    found = False

    for item in items:
        if str(item["product_id"]) == context.product_id:
            expect(item["quantity"]).equal_to(int(quantity))
            found = True
            break

    expect(found).equal_to(True)


@then('I should receive an error message containing "{message}"')
def step_impl(context, message):
    """Check that the response contains an error message"""
    expect(context.resp.status_code).not_equal_to(HTTP_200_OK)

    response_json = context.resp.json()
    expect("message" in response_json).equal_to(True)
    expect(message.lower() in response_json["message"].lower()).equal_to(True)


@when(
    'I click the "Update Quantity" button for product "{product_id}" in order "{order_id}"'
)
def step_impl(context, product_id, order_id):
    """Click the Update Quantity button for a specific product in an order"""
    # Find the button by its data attributes
    button_selector = f"button.update-quantity-btn[data-order-id='{order_id}'][data-product-id='{product_id}']"

    # Wait for the button to be clickable
    button = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
    )

    # Click the button
    button.click()

    # Store the order_id and product_id for later steps
    context.order_id = order_id
    context.product_id = product_id


@then("I should see the update quantity form")
def step_impl(context):
    """Check that the update quantity form is visible"""
    # Wait for the form to be visible
    form = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located((By.ID, "update_item_form"))
    )

    # Check that the form is displayed
    expect(form.is_displayed()).equal_to(True)

    # Check that the product ID field has the correct value
    product_id_field = context.driver.find_element(By.ID, "update_product_id")
    expect(product_id_field.get_attribute("value")).equal_to(context.product_id)

    # Check that the order ID field has the correct value
    order_id_field = context.driver.find_element(By.ID, "update_order_id")
    expect(order_id_field.get_attribute("value")).equal_to(context.order_id)


@then(
    'I should see "{quantity}" as the quantity for product "{product_id}" in order "{order_id}"'
)
def step_impl(context, quantity, product_id, order_id):
    """Check that the product has the expected quantity in the UI"""
    # Wait for the page to refresh and show the updated quantity
    WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "#search_results table")
        )
    )

    # Find the cell containing the quantity for the specified product
    # This is a bit complex because we need to find the right nested table and row
    # First, find the order row
    order_row = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, f"//tr[td[contains(text(), '{order_id}')]]")
        )
    )

    # Within that row, find the nested table with order items
    items_table = order_row.find_element(By.CSS_SELECTOR, "table.table-bordered")

    # Find the row for the specific product
    product_row = items_table.find_element(
        By.XPATH, f".//tr[td[contains(text(), '{product_id}')]]"
    )

    # Get the quantity cell (second cell in the row)
    quantity_cell = product_row.find_elements(By.TAG_NAME, "td")[1]

    # Check that the quantity matches
    expect(quantity_cell.text).equal_to(quantity)
