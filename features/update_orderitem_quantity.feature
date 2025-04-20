Feature: Update Order Item Quantity
    As a Customer
    I need to be able to update the quantity of items in my orders
    So that I can adjust my order without having to create a new one

Background:
    Given the following orders
        | customer_id | order_status | order_created | order_updated |
        | 1           | PENDING      | 2023-10-01    | 2023-10-02    |
        | 2           | SHIPPED      | 2023-10-03    | 2023-10-04    |
    And the following order items
        | order_id | product_id | quantity | price  |
        | 1        | 101        | 2        | 19.99  |
        | 1        | 102        | 1        | 29.99  |
        | 2        | 103        | 3        | 9.99   |

Scenario: Update an order item quantity
    When I update the quantity of product "101" in order "1" to "5"
    Then the order item should have a quantity of "5"
    And the response status code should be "200"

Scenario: Update an order item with invalid quantity
    When I update the quantity of product "101" in order "1" to "-1"
    Then I should receive an error message containing "Invalid"
    And the response status code should be "400"

Scenario: Update an order item that doesn't exist
    When I update the quantity of product "999" in order "1" to "5"
    Then I should receive an error message containing "not found"
    And the response status code should be "404"

Scenario: Update an order item via the web UI
    When I visit the "Home Page"
    And I enter "1" in the "history_customer_id" field
    And I press the "View History" button
    Then I should see "101" in the results
    When I click the "Update Quantity" button for product "101" in order "1"
    Then I should see the update quantity form
    When I enter "5" in the "update_quantity" field
    And I press the "Update Item" button
    Then I should see the message "Item quantity updated successfully"
    And I should see "5" as the quantity for product "101" in order "1"
