// This js file is used to hold code used to manipulate the video e.g. pause, stop etc.
var pauseButton, muteButton;
var paused = false;
var muted = false;

// used to pause the video stream. Also flips the icon on the pause button to indicate what the button
// will do
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

// controls sound and handles the flipping of the buttons
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

// if the user presses the enter button, then we will send a message and reset the message field
function buttonPress(e) {
    if (e.keyCode == 13) {
        e.preventDefault(); // stop the line break being added
        sendMessage();
        var messageField = document.getElementById("message-field");
        messageField = messageField.value = "";
    }
}

