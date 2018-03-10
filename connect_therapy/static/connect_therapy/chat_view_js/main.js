window.onload = function () {
    hideVideoControls()
    hideUploadDownloadControls()
};

function hideUploadDownloadControls() {
    document.getElementById("download-form").style.display = "none";
    document.getElementById("uploaded-table").style.display = "none";
}

function hideVideoControls() {
    document.getElementById("controls").style.visibility = "hidden";
    document.getElementById("wait-for-peer-to-connect").style.visibility = "hidden";
    pauseButton = document.getElementById("paused");
    muteButton = document.getElementById("muted");
}

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