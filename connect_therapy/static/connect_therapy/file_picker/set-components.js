
function showUpload() {
    // show the upload form and hide the download form
    document.getElementById("upload-form").style.display = "block";
    document.getElementById("download-form").style.display = "none";
}

function showDownload() {
    // Show the download form and hide the upload form
    document.getElementById("upload-form").style.display = "none";
    document.getElementById("download-form").style.display = "block";
}

function hideUploadDownloadControls() {
    document.getElementById("download-form").style.display = "none";
    document.getElementById("uploaded-table").style.display = "none";
}