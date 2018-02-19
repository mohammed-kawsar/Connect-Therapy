// This js file is used to hold code used to manipulate the video e.g. pause, stop etc.
var pauseButton, muteButton;
var paused = false;
var muted = false;
window.onload = function () {
    // hide video controls
    document.getElementById("controls").style.visibility = "hidden";
    document.getElementById("wait-for-peer-to-connect").style.visibility = "hidden";
    pauseButton = document.getElementById("paused");
    muteButton = document.getElementById("muted");
}

function pause() {
    if (paused) {
        paused = false;
        webrtc.resume();
        pauseButton.innerHTML = "⏸";

    } else {
        paused = true;
        webrtc.pause();
        pauseButton.innerHTML = "▶";
    }
}

function mute() {
    if (muted) {
        muted = false;
        webrtc.unmute();
        muteButton.innerHTML = "🔊";
    } else {
        muted = true;
        webrtc.mute();
        muteButton.innerHTML = "🔇";
    }
}

function buttonPress(e) {
    if (e.keyCode == 13) {
        sendMessage();
        document.getElementById("message-field").value = "";
    }
}

