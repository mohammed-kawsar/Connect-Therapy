$(document).ready(function () {
    $("#send-email").click(function (e) {
        e.preventDefault();
        var form = $("#resend_conf_email");
        $.ajax({
            type: "post",
            url: form.attr("form-submit-url"), // get the url from the form object itself
            data: {
                "email_address": $("#id_email_address").val(),
                'csrfmiddlewaretoken': CSRF_TOKEN
            },
            dataType: 'json',
            success: function (data) {
                if (data.validEmailFormat) {
                    $("#check-email").css("display", "none");
                    $("#sent-email").css("display", "block");
                } else {
                    $("#check-email").css("display", "block");
                    $("#sent-email").css("display", "none");
                }
            }
        });
    });
});