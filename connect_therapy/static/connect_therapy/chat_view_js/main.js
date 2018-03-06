window.onload = function () {
    hideVideoControls()
    setUpModal()
};

function setUpModal() {
    var modal = document.getElementById('s3-modal');


    var btn = document.getElementById("s3-modal-button");


    var span = document.getElementsByClassName("close")[0];


    btn.onclick = function () {
        modal.style.display = "block";
    }


    span.onclick = function () {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

function hideVideoControls() {
    document.getElementById("controls").style.visibility = "hidden";
    document.getElementById("wait-for-peer-to-connect").style.visibility = "hidden";
    pauseButton = document.getElementById("paused");
    muteButton = document.getElementById("muted");
}