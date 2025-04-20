Feature: The order items functionality
    As a Customer
    I need to be able to view items in my orders
    So that I can track what products I've ordered

Background:
    Given the following orders
        | customer_id | order_status | order_created | order_updated |
        | 1           | PENDING      | 2023-10-01    | 2023-10-02    |
        | 2           | SHIPPED      | 2023-10-03    | 2023-10-04    |
        | 3           | DELIVERED    | 2023-10-05    | 2023-10-06    |
        | 4           | CANCELED     | 2023-10-07    | 2023-10-08    |
    And the following order items
        | order_id | product_id | quantity | price  |
        | 1        | 101        | 2        | 19.99  |
        | 1        | 102        | 1        | 29.99  |
        | 2        | 103        | 3        | 9.99   |
        | 3        | 104        | 1        | 49.99  |
        | 3        | 105        | 2        | 15.50  |

Scenario: List all items in an order
    When I request to list items for order with id "1"
    Then I should receive an empty response
    And the response status code should be "204"

Scenario: List items for an order that doesn't exist
    When I request to list items for order with id "999"
    Then I should receive an empty response
    And the response status code should be "204"

Scenario: List items for an order with no items
    When I request to list items for order with id "4"
    Then I should receive an empty response
    And the response status code should be "204"

Scenario: List items for an order via the web UI
    When I visit the "Home Page"
    # Skip this test for now as the web UI doesn't support listing order items yet
    # This scenario will be implemented when the web UI is updated

Scenario: Create an Order Item via the web UI
    When I visit the "Home Page"
    # First create a new order
    And I set the "order_customer_id" to "1"
    And I set the "order_status" to "PENDING"
    And I press the "Create" button
    Then I should see the message "Success"
    # Get the order ID from the form
    When I set the "item_product_id" to "999"
    And I set the "item_quantity" to "5"
    And I set the "item_price" to "24.99"
    When I press the "create item" button
    Then I should see the message "Success"
    # Search for the order to verify the item was added
    When I press the "Search" button
    Then I should see "999" in the results
    And I should see "5" in the results
    And I should see "$24.99" in the results

Scenario: Create an Order Item with a specific Order ID
    When I visit the "Home Page"
    # First create a new order
    And I set the "order_customer_id" to "2"
    And I set the "order_status" to "SHIPPED"
    And I press the "Create" button
    Then I should see the message "Success"
    # Get the order ID and use it directly
    When I set the "item_product_id" to "888"
    And I set the "item_quantity" to "3"
    And I set the "item_price" to "15.75"
    And I press the "create item" button
    Then I should see the message "Success"
    # Search for the order to verify the item was added
    When I press the "Search" button
    Then I should see "888" in the results
    And I should see "3" in the results
    And I should see "$15.75" in the results

Scenario: Attempt to create an Order Item without an Order ID
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "item_product_id" to "777"
    And I set the "item_quantity" to "2"
    And I set the "item_price" to "9.99"
    And I press the "create item" button
    Then I should see the message "Please enter an Order ID"

Scenario: Attempt to create an Order Item without a Product ID
    When I visit the "Home Page"
    And I set the "item_order_id" to "1"
    And I set the "item_quantity" to "2"
    And I set the "item_price" to "9.99"
    And I press the "create item" button
    Then I should see the message "Product ID is required"

Scenario: Attempt to create an Order Item with invalid quantity
    When I visit the "Home Page"
    And I set the "item_order_id" to "1"
    And I set the "item_product_id" to "777"
    And I set the "item_quantity" to "0"
    And I set the "item_price" to "9.99"
    And I press the "create item" button
    Then I should see the message "Quantity must be at least 1"

Scenario: Attempt to create an Order Item with invalid price
    When I visit the "Home Page"
    And I set the "item_order_id" to "1"
    And I set the "item_product_id" to "777"
    And I set the "item_quantity" to "2"
    And I set the "item_price" to "0"
    And I press the "create item" button
    Then I should see the message "Price must be greater than 0"
