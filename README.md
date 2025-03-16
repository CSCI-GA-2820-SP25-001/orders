# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


## Overview

This repo contains code for the orders microservice. The `/service` folder contains `models.py` file for our model and a `routes.py` file for our service. The `/tests` folder has test cases for testing the model and the service separately.


## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes

## Database

Data for our orders will be compiled in a PostgreSQL database, under the table name "order" located in models/models.py. Features and accepted entries are as follows:

id (Integer)
customer_id (Integer)
order_status (String)
order_created (Datetime)
order_updated (Datetime)
orderitems (Unbounded)


## Functionalities

The following functionalities detail actions users can take when interacting with the orders microservice portion of the website. Functionalities can be found under models/routes.py, and corresponding tests can be found under tests/test_routes.py.

REST API Endpoints:

get_orderitem (Return an Order Item based on its id)
create_order (Create an order)
create_orderitem (Create an item within an order)
get_orders (Return an order based on its id)
list_orders (Return a list of all orders)
delete_orderitem (Delete an item from an order)
delete_order (Delete an order)
update_orders (Update an order)
update_items (Update an item in an order)
list_orderitems (Return a list of all items in a given order)

Utility Functions:

check_content_type (Checks that the media type is correct)


```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
