window.onload = function () {
    hideVideoControls()
    hideUploadDownloadControls()
};


function hideVideoControls() {
    document.getElementById("controls").style.visibility = "hidden";
    document.getElementById("wait-for-peer-to-connect").style.visibility = "hidden";
    pauseButton = document.getElementById("paused");
    muteButton = document.getElementById("muted");
}
