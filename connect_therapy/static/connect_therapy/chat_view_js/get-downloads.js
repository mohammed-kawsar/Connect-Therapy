function getDownloadsAJAX() {
    // Disable the refresh button for 15 seconds to prevent the user
    // from constantly sending AJAX requests to the server
    document.getElementById("download-refresh-button").disabled = true;
    setTimeout(function () {
        document.getElementById("download-refresh-button").disabled = false;
    }, 15000);
    $.ajax({
        url: ajax_download_url, // use the global variable we defined in chat.html
        type: "get", //send it through get method
        success: function (response) {
            // if successful, we will first empty the table and then add the data to the table
            $("#download-table td").remove();
            var files = response.downloadable_files;
            Object.keys(files).forEach(function (key) {
                $("#download-table").prepend(
                    "<tr><td><a target='_blank' href=" + files[key] + ">" + key.split('/')[1] + "</a></td></tr>"
                )
                console.log(files[key]);
            });
        },
        error: function (xhr) {
            console.log("Got an error back");
        }
    });
}

