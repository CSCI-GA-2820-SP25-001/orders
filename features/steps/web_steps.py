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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import re
import logging
from typing import Any
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException, WebDriverException

ID_PREFIX = "pet_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')


@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = context.driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = context.driver.find_element(By.ID, element_id)

    element.clear()
    element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = Select(context.driver.find_element(By.ID, element_id))
    except NoSuchElementException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context: Any, text: str, element_name: str) -> None:
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = Select(context.driver.find_element(By.ID, element_id))
    except NoSuchElementException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = context.driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    except WebDriverException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    except WebDriverException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    print(f"Looking for button with ID: {button_id}")
    try:
        element = context.driver.find_element(By.ID, button_id)
        print(f"Found button with ID: {button_id}")
        element.click()
        print(f"Clicked button with ID: {button_id}")
    except WebDriverException as e:
        print(f"Error clicking button with ID {button_id}: {str(e)}")
        # List all buttons on the page
        buttons = context.driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons on the page:")
        for btn in buttons:
            print(f"  Button ID: {btn.get_attribute('id')}, Text: {btn.text}")
        raise


@then('I should see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    found = WebDriverWait(context.driver, wait_time).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "search_results"), name
        )
    )
    assert found


@then('I should not see "{name}" in the results')
def step_impl(context: Any, name: str) -> None:
    element = context.driver.find_element(By.ID, "search_results")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    save_screenshot(context, message)
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    print(f"Looking for message: '{message}' in flash_message element")
    try:
        found = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.text_to_be_present_in_element(
                (By.ID, "flash_message"), message
            )
        )
        print(f"Found message: '{message}' in flash_message element")
        assert found
    except WebDriverException as e:
        print(f"Error finding message '{message}': {str(e)}")
        # Get the actual message
        try:
            flash_message = context.driver.find_element(By.ID, "flash_message")
            print(f"Actual message in flash_message element: '{flash_message.text}'")
        except NoSuchElementException:
            print("Could not find flash_message element")
        raise


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        found = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.text_to_be_present_in_element_value(
                (By.ID, element_id), text_string
            )
        )
    except WebDriverException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        found = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.text_to_be_present_in_element_value(
                (By.ID, element_id), text_string
            )
        )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    # Use a shorter wait time for better performance
    wait_time = min(context.wait_seconds, 3)
    # First try with the ID_PREFIX (for backward compatibility)
    try:
        element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    except WebDriverException:
        # If not found, try without the prefix (for our new elements)
        element_id = element_name.lower().replace(" ", "_")
        element = WebDriverWait(context.driver, wait_time).until(
            expected_conditions.presence_of_element_located((By.ID, element_id))
        )
    element.clear()
    element.send_keys(text_string)
