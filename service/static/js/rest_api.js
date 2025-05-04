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
        // Also update the order ID field in the order item section
        $("#item_order_id").val(res.id);
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
            // Display the order in the search results
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Created</th>'
            table += '<th class="col-md-2">Updated</th>'
            table += '<th class="col-md-2">Order Items</th>'
            table += '<th class="col-md-1">Actions</th>'
            table += '</tr></thead><tbody>'
            
            // Get the date value
            let created = res.order_created ? res.order_created.split('T')[0] : "";
            let updated = res.order_updated ? res.order_updated.split('T')[0] : "";
            
            // Add a cancel button if the order is in pending status
            let actionButtons = '';
            if (res.order_status.toLowerCase() === 'pending') {
                actionButtons = `<button class="btn btn-danger btn-sm cancel-order-btn" data-id="${res.id}">Cancel Order</button>`;
            } else {
                actionButtons = `<em>No actions available</em>`;
            }
            
            // Add order items details
            let itemsCell = '';
            if (res.orderitems && res.orderitems.length > 0) {
                itemsCell += '<table class="table table-bordered table-sm">';
                itemsCell += '<thead><tr><th>ID</th><th>Product ID</th><th>Quantity</th><th>Price</th></tr></thead>';
                itemsCell += '<tbody>';
                
                for (let j = 0; j < res.orderitems.length; j++) {
                    let item = res.orderitems[j];
                    itemsCell += `<tr>
                        <td>${item.id}</td>
                        <td>${item.product_id}</td>
                        <td>${item.quantity}</td>
                        <td>$${item.price.toFixed(2)}</td>
                    </tr>`;
                }
                
                itemsCell += '</tbody></table>';
            } else {
                itemsCell = '<em>No items in this order</em>';
            }
            
            table += `<tr>
                <td>${res.id}</td>
                <td>${res.customer_id}</td>
                <td>${res.order_status}</td>
                <td>${created}</td>
                <td>${updated}</td>
                <td>${itemsCell}</td>
                <td>${actionButtons}</td>
            </tr>`;
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
        $("#item_order_id").val("");
        $("#item_product_id").val("");
        $("#item_quantity").val("1");
        $("#item_price").val("");
        $("#flash_message").empty();
        $("#search_results").empty();
        clear_form_data()
    });

    // ****************************************
    // Create an Order Item 
    // ****************************************

    $("#create_item-btn").click(function () {
        let order_id = $("#item_order_id").val();
        
        if (!order_id) {
            flash_message("Please enter an Order ID");
            return;
        }
        
        let product_id = $("#item_product_id").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();
        
        if (!product_id) {
            flash_message("Product ID is required");
            return;
        }
        
        if (!quantity || quantity < 1) {
            flash_message("Quantity must be at least 1");
            return;
        }
        
        if (!price || price <= 0) {
            flash_message("Price must be greater than 0");
            return;
        }
        
        let data = {
            "product_id": parseInt(product_id),
            "quantity": parseInt(quantity),
            "price": parseFloat(price)
        };
        
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/orders/${order_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });
        
        ajax.done(function(res){
            console.log("Order item created successfully:", res);
            // Clear the item form fields
            $("#item_product_id").val("");
            $("#item_quantity").val("1");
            $("#item_price").val("");
            
            // Refresh the order to show the new item
            let retrieveAjax = $.ajax({
                type: "GET",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: ''
            });
            
            retrieveAjax.done(function(orderRes){
                console.log("Success:", orderRes);
                update_form_data(orderRes);
                flash_message("Success");
            });
            
            retrieveAjax.fail(function(err){
                console.error("Failed to refresh order details:", err);
                flash_message("Order item created, but failed to refresh order details");
            });
        });
        
        ajax.fail(function(res){
            console.error("Failed to create order item:", res);
            flash_message(res.responseJSON ? res.responseJSON.message : "Error creating order item");
        });
    });

    // ****************************************
    // Cancel an Order
    // ****************************************

    $("#cancel-btn").click(function () {
        let order_id = $("#order_id").val();

        if (!order_id) {
            flash_message("Please enter an Order ID to cancel");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Order has been successfully canceled!");
        });

        ajax.fail(function(res){
            if (res.status === 409) {
                flash_message("This order cannot be canceled because it is not in 'pending' status.");
            } else if (res.status === 404) {
                flash_message("Order not found with the given ID");
            } else {
                flash_message("Server error!");
            }
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
            table += '<th class="col-md-1">Created</th>'
            table += '<th class="col-md-1">Updated</th>'
            table += '<th class="col-md-3">Order Items</th>'
            table += '<th class="col-md-2">Actions</th>'
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
                    row += '<thead><tr><th>Product ID</th><th>Quantity</th><th>Price</th></tr></thead>';
                    row += '<tbody>';
                    
                    for (let j = 0; j < order.orderitems.length; j++) {
                        let item = order.orderitems[j];
                        row += `<tr>
                            <td>${item.product_id}</td>
                            <td>${item.quantity}</td>
                            <td>$${item.price.toFixed(2)}</td>
                        </tr>`;
                    }
                    
                    row += '</tbody></table>';
                } else {
                    row += '<em>No items in this order</em>';
                }
                
                row += '</td>';
                
                // Add a cancel button if the order is in pending status
                let actionButtons = '';
                if (order.order_status.toLowerCase() === 'pending') {
                    actionButtons = `<button class="btn btn-danger btn-sm cancel-order-btn" data-id="${order.id}">Cancel Order</button>`;
                } else {
                    actionButtons = `<em>No actions available</em>`;
                }
                
                row += `<td>${actionButtons}</td></tr>`;
                table += row;
                
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

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
    // Update an Order Item Quantity
    // ****************************************

    $("#update_item-btn").click(function () {
        let order_id = $("#item_order_id").val();
        let item_id = $("#item_id").val();
        let quantity = $("#item_quantity").val();
        
        if (!order_id) {
            flash_message("Please enter an Order ID");
            return;
        }
        
        if (!item_id) {
            flash_message("Please enter an Item ID");
            return;
        }
        
        if (!quantity || quantity < 1) {
            flash_message("Quantity must be at least 1");
            return;
        }
        
        // First, get the current item to preserve other fields
        $("#flash_message").empty();
        
        let getItemAjax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });
        
        getItemAjax.done(function(currentItem) {
            // Now update with the new quantity
            let data = {
                "order_id": parseInt(order_id),
                "product_id": currentItem.product_id,
                "quantity": parseInt(quantity),
                "price": currentItem.price
            };
            
            let updateAjax = $.ajax({
                type: "PUT",
                url: `/orders/${order_id}/items/${item_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            });
            
            updateAjax.done(function(res) {
                // Clear the item ID field
                $("#item_id").val("");
                
                // Refresh the order to show the updated item
                let retrieveAjax = $.ajax({
                    type: "GET",
                    url: `/orders/${order_id}`,
                    contentType: "application/json",
                    data: ''
                });
                
                retrieveAjax.done(function(orderRes) {
                    update_form_data(orderRes);
                    
                    // If the order is currently displayed in search results, update it there too
                    if ($("#search_results").html().includes(`Order ID: ${order_id}`)) {
                        $("#retrieve-btn").click(); // Refresh the display
                    }
                    
                    flash_message("Item quantity updated successfully");
                });
                
                retrieveAjax.fail(function(err) {
                    flash_message("Item quantity updated, but failed to refresh order details");
                });
            });
            
            updateAjax.fail(function(res) {
                if (res.status === 400) {
                    flash_message("Invalid quantity. Please check stock limits.");
                } else if (res.status === 404) {
                    flash_message("Order item not found");
                } else {
                    flash_message("Error updating item quantity");
                }
            });
        });
        
        getItemAjax.fail(function(res) {
            flash_message("Failed to retrieve item. Please check the Order ID and Item ID.");
        });
    });

    // ****************************************
    // Handle Cancel Order button clicks in search results
    // ****************************************
    
    // Use event delegation for dynamically created cancel buttons
    $(document).on('click', '.cancel-order-btn', function() {
        let order_id = $(this).data('id');
        
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: ''
        });
        
        ajax.done(function(res) {
            // Update the status in the table row
            let row = $(`.cancel-order-btn[data-id="${order_id}"]`).closest('tr');
            row.find('td:nth-child(3)').text('canceled'); // Update status cell
            
            // Replace the cancel button with "No actions available"
            $(`.cancel-order-btn[data-id="${order_id}"]`).parent().html('<em>No actions available</em>');
            
            // If this order is currently loaded in the form, update the form too
            if ($("#order_id").val() == order_id) {
                update_form_data(res);
            }
            
            flash_message("Order has been successfully canceled!");
        });
        
        ajax.fail(function(res) {
            if (res.status === 409) {
                flash_message("This order cannot be canceled because it is not in 'pending' status.");
            } else if (res.status === 404) {
                flash_message("Order not found with the given ID");
            } else {
                flash_message("Server error!");
            }
        });
    });

    // ****************************************
    // Search for Items within an Order
    // ****************************************

    // Show the item search section when an order is retrieved
    $("#retrieve-btn").click(function() {
        // The search section will be shown after the order is successfully retrieved
        // This is handled in the ajax.done function of the retrieve-btn click handler
    });

    // Handle real-time search as user types in the search box
    $("#item_search").on('input', function() {
        let order_id = $("#item_order_id").val();
        let search_term = $(this).val();
        
        if (!order_id) {
            flash_message("Please retrieve an order first");
            return;
        }
        
        // Make AJAX call to search items
        searchOrderItems(order_id, search_term);
    });

    // Function to search order items
    function searchOrderItems(order_id, search_term) {
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}/items?search=${encodeURIComponent(search_term)}`,
            contentType: "application/json",
            data: ''
        });
        
        ajax.done(function(res) {
            // Clear previous results
            $("#item_search_results_body").empty();
            
            if (res.length > 0) {
                // Hide the "No items found" message
                $("#no_items_found").hide();
                
                // Add each item to the results table
                for (let i = 0; i < res.length; i++) {
                    let item = res[i];
                    let row = `<tr>
                        <td>${item.id}</td>
                        <td>${item.product_id}</td>
                        <td>${item.quantity}</td>
                        <td>$${item.price.toFixed(2)}</td>
                    </tr>`;
                    $("#item_search_results_body").append(row);
                }
            } else {
                // Show the "No items found" message
                $("#no_items_found").show();
            }
        });
        
        ajax.fail(function(res) {
            console.error("Failed to search items:", res);
            flash_message("Error searching items");
        });
    }

    // Modify the retrieve-btn click handler to show the item search section
    // This is done by adding code to the ajax.done function
    $("#retrieve-btn").click(function() {
        // The existing code remains unchanged
        // We're just adding functionality to show the search section after a successful retrieval
        let order_id = $("#order_id").val();
        
        // The original AJAX call is already defined in the retrieve-btn click handler
        // We're just adding to the ajax.done function to show the search section
        
        // After the order is successfully retrieved, show the item search section
        let originalAjax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        });
        
        originalAjax.done(function(res) {
            // Show the item search section
            $("#order_items_search").show();
            
            // Clear any previous search
            $("#item_search").val('');
            $("#item_search_results_body").empty();
            $("#no_items_found").hide();
            
            // If the order has items, populate the search results with all items initially
            if (res.orderitems && res.orderitems.length > 0) {
                for (let i = 0; i < res.orderitems.length; i++) {
                    let item = res.orderitems[i];
                    let row = `<tr>
                        <td>${item.id}</td>
                        <td>${item.product_id}</td>
                        <td>${item.quantity}</td>
                        <td>$${item.price.toFixed(2)}</td>
                    </tr>`;
                    $("#item_search_results_body").append(row);
                }
            } else {
                // Show the "No items found" message
                $("#no_items_found").show();
            }
        });
    });

    // Hide the item search section when clearing the form
    $("#clear-btn").click(function() {
        // Hide the item search section
        $("#order_items_search").hide();
    });

})
