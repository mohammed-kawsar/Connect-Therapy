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

function closeSessionPractitioner() {
    var leave = confirm("Are you sure you want to leave this session?");
    if (leave) {
        window.location.replace(practitioner_notes_url);
    }

}

function closeSessionPatient() {
    var leave = confirm("Are you sure you want to leave this session?");
    if (leave) {
        window.location.replace(patient_notes_url);
    }
}