var webrtc = new SimpleWebRTC({
    // the id/element dom element that will hold "our" video
    localVideoEl: 'localVideo',
    // the id/element dom element that will hold remote videos
    remoteVideosEl: 'remotesVideos',
    // immediately ask for camera access
    autoRequestMedia: true
});

// we have to wait until it's ready
webrtc.on('readyToCall', function() {
    // you can name it anything
    webrtc.joinRoom('50nxJYe'); // tempname

});

function sendMessage() {
    var messageToSend = prompt("Message to send:");
    webrtc.sendToAll("chat", {
        message: messageToSend
    });
    alert("Clicked send");
}

webrtc.connection.on("message", function(data) {
    if (data.type === "chat") {
        document.getElementById("latest-message").innerHTML = data.payload.message;
    }
});