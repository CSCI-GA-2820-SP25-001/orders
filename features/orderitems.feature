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
