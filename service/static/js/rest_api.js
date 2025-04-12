$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#pet_id").val(res.id);
        $("#pet_name").val(res.name);
        $("#pet_category").val(res.category);
        if (res.available == true) {
            $("#pet_available").val("true");
        } else {
            $("#pet_available").val("false");
        }
        $("#pet_gender").val(res.gender);
        $("#pet_birthday").val(res.birthday);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#pet_name").val("");
        $("#pet_category").val("");
        $("#pet_available").val("");
        $("#pet_gender").val("");
        $("#pet_birthday").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

})
