window.onload = function () {
    hideVideoControls()
    hideUploadDownloadControls()
};

function hideUploadDownloadControls() {
    document.getElementById("download-form").style.display = "none";
}

function hideVideoControls() {
    document.getElementById("controls").style.visibility = "hidden";
    document.getElementById("wait-for-peer-to-connect").style.visibility = "hidden";
    pauseButton = document.getElementById("paused");
    muteButton = document.getElementById("muted");
}

function showUpload() {
    document.getElementById("upload-form").style.display = "block";
    document.getElementById("download-form").style.display = "none";
}

function showDownload() {
    document.getElementById("upload-form").style.display = "none";
    document.getElementById("download-form").style.display = "block";
}