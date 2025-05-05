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
            
            // Add action buttons if the order is in pending status
            let actionButtons = '';
            if (res.order_status.toLowerCase() === 'pending') {
                actionButtons = `
                    <button class="btn btn-primary btn-sm edit-order-btn" data-id="${res.id}">Edit Order</button>
                    <button class="btn btn-danger btn-sm cancel-order-btn" data-id="${res.id}">Cancel Order</button>
                `;
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
                
                // Add action buttons if the order is in pending status
                let actionButtons = '';
                if (order.order_status.toLowerCase() === 'pending') {
                    actionButtons = `
                        <button class="btn btn-primary btn-sm edit-order-btn" data-id="${order.id}">Edit Order</button>
                        <button class="btn btn-danger btn-sm cancel-order-btn" data-id="${order.id}">Cancel Order</button>
                    `;
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
    // Edit Order Modal Functionality
    // ****************************************
    
    // Global variable to store the current order being edited
    let currentEditOrder = null;
    
    // Function to update the edit order flash message
    function edit_order_flash_message(message) {
        $("#edit-order-flash-message").empty();
        $("#edit-order-flash-message").append(message);
    }
    
    // Function to refresh the items list in the edit order modal
    function refreshEditOrderItemsList() {
        if (!currentEditOrder || !currentEditOrder.orderitems) {
            return;
        }
        
        let itemsList = $("#edit-order-items-list");
        itemsList.empty();
        
        if (currentEditOrder.orderitems.length === 0) {
            itemsList.append('<p><em>No items in this order</em></p>');
            return;
        }
        
        let table = '<table class="table table-bordered table-sm">';
        table += '<thead><tr><th>ID</th><th>Product ID</th><th>Quantity</th><th>Price</th><th>Actions</th></tr></thead>';
        table += '<tbody>';
        
        for (let i = 0; i < currentEditOrder.orderitems.length; i++) {
            let item = currentEditOrder.orderitems[i];
            table += `<tr>
                <td>${item.id}</td>
                <td>${item.product_id}</td>
                <td>${item.quantity}</td>
                <td>$${item.price.toFixed(2)}</td>
                <td>
                    <button class="btn btn-danger btn-xs remove-item-btn" data-id="${item.id}">Remove</button>
                </td>
            </tr>`;
        }
        
        table += '</tbody></table>';
        itemsList.append(table);
    }
    
    // Handle Edit Order button clicks
    $(document).on('click', '.edit-order-btn', function() {
        let order_id = $(this).data('id');
        
        // Fetch the order details
        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        });
        
        ajax.done(function(res) {
            // Store the current order being edited
            currentEditOrder = res;
            
            // Populate the modal with order details
            $("#edit-order-id").text(res.id);
            $("#edit-customer-id").text(res.customer_id);
            $("#edit-order-status").text(res.order_status);
            
            // Refresh the items list
            refreshEditOrderItemsList();
            
            // Clear the add new item form
            $("#new-product-id").val("");
            $("#new-quantity").val("1");
            $("#new-price").val("");
            
            // Clear any previous flash messages
            edit_order_flash_message("");
            
            // Show the modal
            $("#edit-order-modal").modal('show');
        });
        
        ajax.fail(function(res) {
            flash_message("Failed to retrieve order details. Please try again.");
        });
    });
    
    // Handle Remove Item button clicks in the edit order modal
    $(document).on('click', '.remove-item-btn', function() {
        let item_id = $(this).data('id');
        let order_id = currentEditOrder.id;
        
        // Confirm before removing
        if (!confirm("Are you sure you want to remove this item from the order?")) {
            return;
        }
        
        // Send DELETE request to remove the item
        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });
        
        ajax.done(function() {
            // Remove the item from the currentEditOrder object
            currentEditOrder.orderitems = currentEditOrder.orderitems.filter(item => item.id !== parseInt(item_id));
            
            // Refresh the items list
            refreshEditOrderItemsList();
            
            edit_order_flash_message("Item removed successfully");
        });
        
        ajax.fail(function(res) {
            edit_order_flash_message("Failed to remove item. Please try again.");
        });
    });
    
    // Handle Add New Item button click in the edit order modal
    $("#add-new-item-btn").click(function() {
        let order_id = currentEditOrder.id;
        let product_id = $("#new-product-id").val();
        let quantity = $("#new-quantity").val();
        let price = $("#new-price").val();
        
        // Validate inputs
        if (!product_id) {
            edit_order_flash_message("Product ID is required");
            return;
        }
        
        if (!quantity || quantity < 1) {
            edit_order_flash_message("Quantity must be at least 1");
            return;
        }
        
        if (!price || price <= 0) {
            edit_order_flash_message("Price must be greater than 0");
            return;
        }
        
        let data = {
            "product_id": parseInt(product_id),
            "quantity": parseInt(quantity),
            "price": parseFloat(price)
        };
        
        // Send POST request to add the item
        let ajax = $.ajax({
            type: "POST",
            url: `/orders/${order_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });
        
        ajax.done(function(res) {
            // Add the new item to the currentEditOrder object
            currentEditOrder.orderitems.push(res);
            
            // Refresh the items list
            refreshEditOrderItemsList();
            
            // Clear the form
            $("#new-product-id").val("");
            $("#new-quantity").val("1");
            $("#new-price").val("");
            
            edit_order_flash_message("Item added successfully");
        });
        
        ajax.fail(function(res) {
            if (res.status === 400) {
                edit_order_flash_message("Invalid input. Please check your values.");
            } else if (res.status === 404) {
                edit_order_flash_message("Order not found");
            } else {
                edit_order_flash_message("Failed to add item. Please try again.");
            }
        });
    });
    
    // Handle Save Changes button click in the edit order modal
    $("#save-order-changes-btn").click(function() {
        // Close the modal
        $("#edit-order-modal").modal('hide');
        
        // Refresh the order display to show the updated items
        if ($("#order_id").val() == currentEditOrder.id) {
            $("#retrieve-btn").click();
        } else {
            // If we're in search results, refresh the search
            $("#search-btn").click();
        }
        
        flash_message("Order updated successfully");
    });

})
