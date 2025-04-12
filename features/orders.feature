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
