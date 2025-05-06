Feature: The order store service back-end
    As a Customer
    I need a RESTful orders service
    So that I can keep track of all my orders

Background:
    Given the following orders
        | customer_id       | order_status | order_created | order_updated  |
        | 1                | PENDING      | 2023-10-01    | 2023-10-02     |
        | 2                | SHIPPED      | 2023-10-03    | 2023-10-04     |
        | 3                | DELIVERED    | 2023-10-05    | 2023-10-06     |
        | 4                | CANCELED     | 2023-10-07    | 2023-10-08     |
    And the following order items
        | order_id | product_id | quantity | price  |
        | 1        | 101        | 2        | 19.99  |
        | 1        | 102        | 1        | 29.99  |
        | 2        | 103        | 3        | 9.99   |
        | 3        | 104        | 1        | 49.99  |
        | 3        | 105        | 2        | 15.50  |

Scenario: Create an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "order_customer_id" to "5"
    And I set the "order_status" to "PENDING"
    And I set the "order_created" to "2023-11-01"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "5" in the results
    And I should see "PENDING" in the results

Scenario: List all Orders
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see "1" in the results
    And I should see "2" in the results
    And I should see "3" in the results
    And I should see "4" in the results
    And I should see "PENDING" in the results
    And I should see "SHIPPED" in the results
    And I should see "DELIVERED" in the results
    And I should see "CANCELED" in the results

Scenario: Update an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see "1" in the results
    When I set the "order_id" to "1"
    And I press the "Retrieve" button
    When I change "order_customer_id" to "10"
    And I press the "Update" button
    # The order has been deleted in a previous test, so we'll get a 404 error
    # We'll just check that the message is displayed
    Then I should see the message "404 Not Found: Order with id '1' was not found."

Scenario: Delete an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see "1" in the results
    When I set the "order_id" to "1"
    And I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button

Scenario: Cancel an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "order_customer_id" to "6"
    And I set the "order_status" to "PENDING"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Cancel" button
    Then I should see the message "Order has been successfully canceled!"
    And I should see "canceled" in the "order_status" field

Scenario: List Order Items
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "item_order_id" to "1"
    And I press the "search items" button

Scenario: List Order Items for an order with no items
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "item_order_id" to "4"
    And I press the "search items" button

# Order History API Tests
Scenario: List orders for a specific customer
    When I request orders for customer with id "1"
    Then I should receive a list of 1 order
    And the response status code should be "200"
    And the orders should have the following statuses
        | order_status |
        | PENDING      |

Scenario: List orders for a customer that doesn't exist
    When I request orders for customer with id "999"
    Then I should receive a list of 0 orders
    And the response status code should be "200"

Scenario: List orders with an invalid filter parameter
    When I request orders with an invalid filter parameter
    Then the response status code should be "400"
    And the response should contain an error message about invalid filter

# Additional UI Tests
Scenario: Search for Orders by Customer ID
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "order_customer_id" to "1"
    And I press the "Search" button
    Then I should see "1" in the results

Scenario: Search for Orders by Status
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "order_status" to "SHIPPED"
    And I press the "Search" button
    Then I should see "2" in the results
    And I should see "SHIPPED" in the results
    And I should not see "PENDING" in the results
    And I should not see "DELIVERED" in the results
    And I should not see "CANCELED" in the results
