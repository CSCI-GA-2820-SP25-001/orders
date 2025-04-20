$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_customer_id").val(res.customer_id);
        $("#order_status").val(res.order_status);
        if (res.order_created) {
            $("#order_created").val(res.order_created.split('T')[0]);
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_customer_id").val("");
        $("#order_status").val("");
        $("#order_created").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Show the update item form with the item data
    function show_update_item_form(order_id, item) {
        // Fill in the form fields
        $("#update_order_id").val(order_id);
        $("#update_item_id").val(item.id);
        $("#update_product_id").val(item.product_id);
        $("#update_price").val(item.price.toFixed(2));
        $("#update_quantity").val(item.quantity);
        
        // Show the form
        $("#update_item_form").show();
        
        // Scroll to the form
        $('html, body').animate({
            scrollTop: $("#update_item_form").offset().top
        }, 500);
    }

    // Hide the update item form
    function hide_update_item_form() {
        $("#update_item_form").hide();
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#order_customer_id").val();
        let order_status = $("#order_status").val();
        let order_created = $("#order_created").val();

        let data = {
            "customer_id": customer_id,
            "order_status": order_status,
            "order_created": order_created
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let customer_id = $("#order_customer_id").val();
        let order_status = $("#order_status").val();
        
        // Get current timestamp for order_updated
        let current_date = new Date();
        let order_updated = current_date.toISOString();

        let data = {
            "customer_id": customer_id,
            "order_status": order_status,
            "order_updated": order_updated
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search for an Order by ID
    // ****************************************

    $("#search-by-id-btn").click(function () {

        let order_id = $("#search_order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            // Display the order in the search results
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-3">Customer ID</th>'
            table += '<th class="col-md-3">Status</th>'
            table += '<th class="col-md-3">Created</th>'
            table += '<th class="col-md-3">Updated</th>'
            table += '</tr></thead><tbody>'
            
            // Get the date value
            let created = res.order_created ? res.order_created.split('T')[0] : "";
            let updated = res.order_updated ? res.order_updated.split('T')[0] : "";
            
            table += `<tr><td>${res.id}</td><td>${res.customer_id}</td><td>${res.order_status}</td><td>${created}</td><td>${updated}</td></tr>`;
            table += '</tbody></table>';
            $("#search_results").append(table);
            
            // Also update the form with the order data
            update_form_data(res);
            
            flash_message("Order found successfully")
        });

        ajax.fail(function(res){
            clear_form_data();
            $("#search_results").empty();
            flash_message("Order not found with the given ID")
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#search_order_id").val("");
        $("#history_customer_id").val("");
        $("#flash_message").empty();
        $("#search_results").empty();
        clear_form_data()
        hide_update_item_form();
    });

    // ****************************************
    // View Order History by Customer ID
    // ****************************************

    $("#view-history-btn").click(function () {
        let customer_id = $("#history_customer_id").val();
        
        if (!customer_id) {
            flash_message("Please enter a Customer ID to view order history");
            return;
        }

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "GET",
            url: `/orders?customer=${customer_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results").empty();
            
            if (res.length === 0) {
                flash_message(`No orders found for Customer ID: ${customer_id}`);
                return;
            }
            
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Created</th>'
            table += '<th class="col-md-2">Updated</th>'
            table += '<th class="col-md-3">Order Items</th>'
            table += '</tr></thead><tbody>'
            
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                let created = order.order_created ? order.order_created.split('T')[0] : "";
                let updated = order.order_updated ? order.order_updated.split('T')[0] : "";
                
                // Create a row for the order
                let row = `<tr id="row_${i}">
                    <td>${order.id}</td>
                    <td>${order.customer_id}</td>
                    <td>${order.order_status}</td>
                    <td>${created}</td>
                    <td>${updated}</td>
                    <td>`;
                
                // Add order items details
                if (order.orderitems && order.orderitems.length > 0) {
                    row += '<table class="table table-bordered table-sm">';
                    row += '<thead><tr><th>Product ID</th><th>Quantity</th><th>Price</th><th>Actions</th></tr></thead>';
                    row += '<tbody>';
                    
                    for (let j = 0; j < order.orderitems.length; j++) {
                        let item = order.orderitems[j];
                        row += `<tr>
                            <td>${item.product_id}</td>
                            <td>${item.quantity}</td>
                            <td>$${item.price.toFixed(2)}</td>
                            <td><button class="btn btn-sm btn-primary update-quantity-btn" 
                                data-order-id="${order.id}" 
                                data-item-id="${item.id}" 
                                data-product-id="${item.product_id}" 
                                data-quantity="${item.quantity}" 
                                data-price="${item.price}">Update Quantity</button></td>
                        </tr>`;
                    }
                    
                    row += '</tbody></table>';
                } else {
                    row += '<em>No items in this order</em>';
                }
                
                row += '</td></tr>';
                table += row;
            }
            
            table += '</tbody></table>';
            $("#search_results").append(table);
            
            // Add event listeners to the update quantity buttons
            $(".update-quantity-btn").click(function() {
                let order_id = $(this).data("order-id");
                let item = {
                    id: $(this).data("item-id"),
                    product_id: $(this).data("product-id"),
                    quantity: $(this).data("quantity"),
                    price: $(this).data("price")
                };
                show_update_item_form(order_id, item);
            });
            
            flash_message(`Found ${res.length} order(s) for Customer ID: ${customer_id}`);
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Search for Orders
    // ****************************************

    $("#search-btn").click(function () {

        let customer_id = $("#order_customer_id").val();
        let order_status = $("#order_status").val();
        let order_created = $("#order_created").val();

        let queryString = ""

        if (customer_id) {
            queryString += 'customer=' + customer_id
        }
        if (order_status) {
            if (queryString.length > 0) {
                queryString += '&status=' + order_status
            } else {
                queryString += 'status=' + order_status
            }
        }
        if (order_created) {
            if (queryString.length > 0) {
                queryString += '&created=' + order_created
            } else {
                queryString += 'created=' + order_created
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Created</th>'
            table += '<th class="col-md-2">Updated</th>'
            table += '<th class="col-md-3">Order Items</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                let created = order.order_created ? order.order_created.split('T')[0] : "";
                let updated = order.order_updated ? order.order_updated.split('T')[0] : "";
                
                // Create a row for the order
                let row = `<tr id="row_${i}">
                    <td>${order.id}</td>
                    <td>${order.customer_id}</td>
                    <td>${order.order_status}</td>
                    <td>${created}</td>
                    <td>${updated}</td>
                    <td>`;
                
                // Add order items details
                if (order.orderitems && order.orderitems.length > 0) {
                    row += '<table class="table table-bordered table-sm">';
                    row += '<thead><tr><th>Product ID</th><th>Quantity</th><th>Price</th><th>Actions</th></tr></thead>';
                    row += '<tbody>';
                    
                    for (let j = 0; j < order.orderitems.length; j++) {
                        let item = order.orderitems[j];
                        row += `<tr>
                            <td>${item.product_id}</td>
                            <td>${item.quantity}</td>
                            <td>$${item.price.toFixed(2)}</td>
                            <td><button class="btn btn-sm btn-primary update-quantity-btn" 
                                data-order-id="${order.id}" 
                                data-item-id="${item.id}" 
                                data-product-id="${item.product_id}" 
                                data-quantity="${item.quantity}" 
                                data-price="${item.price}">Update Quantity</button></td>
                        </tr>`;
                    }
                    
                    row += '</tbody></table>';
                } else {
                    row += '<em>No items in this order</em>';
                }
                
                row += '</td></tr>';
                table += row;
                
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // Add event listeners to the update quantity buttons
            $(".update-quantity-btn").click(function() {
                let order_id = $(this).data("order-id");
                let item = {
                    id: $(this).data("item-id"),
                    product_id: $(this).data("product-id"),
                    quantity: $(this).data("quantity"),
                    price: $(this).data("price")
                };
                show_update_item_form(order_id, item);
            });

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update Order Item Quantity
    // ****************************************

    // Increase quantity button
    $("#increase-qty-btn").click(function() {
        let current_qty = parseInt($("#update_quantity").val());
        $("#update_quantity").val(current_qty + 1);
    });

    // Decrease quantity button
    $("#decrease-qty-btn").click(function() {
        let current_qty = parseInt($("#update_quantity").val());
        if (current_qty > 1) {
            $("#update_quantity").val(current_qty - 1);
        }
    });

    // Cancel update button
    $("#cancel-update-btn").click(function() {
        hide_update_item_form();
    });

    // Update item button
    $("#update-item-btn").click(function() {
        let order_id = $("#update_order_id").val();
        let item_id = $("#update_item_id").val();
        let product_id = $("#update_product_id").val();
        let price = parseFloat($("#update_price").val());
        let quantity = parseInt($("#update_quantity").val());

        // Validate quantity
        if (isNaN(quantity) || quantity < 1) {
            flash_message("Quantity must be a positive number");
            return;
        }

        // Prepare data for API call
        let data = {
            "order_id": parseInt(order_id),
            "product_id": parseInt(product_id),
            "quantity": quantity,
            "price": price
        };

        $("#flash_message").empty();

        // Make API call to update the item
        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res) {
            // Hide the update form
            hide_update_item_form();
            
            // Refresh the order display to show updated quantity
            if ($("#history_customer_id").val()) {
                $("#view-history-btn").click();
            } else if ($("#order_customer_id").val() || $("#order_status").val() || $("#order_created").val()) {
                $("#search-btn").click();
            }
            
            flash_message("Item quantity updated successfully");
        });

        ajax.fail(function(res) {
            let error_msg = "Failed to update item quantity";
            if (res.responseJSON && res.responseJSON.message) {
                error_msg = res.responseJSON.message;
            }
            flash_message(error_msg);
        });
    });

})
