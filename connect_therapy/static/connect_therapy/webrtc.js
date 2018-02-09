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
    var messageToSend = document.getElementById("message-field").value;
    if (messageToSend.length > 0) {
        // messageToAdd, tableToAddTo, sent?
        addMessageToTable(messageToSend, document.getElementById("message-table"), true);

         webrtc.sendToAll("chat", {
             message: messageToSend
         });

         document.getElementById("message-field").value = "";
    }
}

function addMessageToTable(message,table,sent) {
    var row = table.insertRow(-1);

    var sender = row.insertCell(0);
    var messageText = row.insertCell(1);
    var timeStamp = row.insertCell(2);

    if (sent == true) {
        sender.innerHTML = "<i>You</i>";
    } else {
        sender.innerHTML = "<i>Them</i>"
    }

    messageText.innerHTML = message;
    timeStamp.innerHTML = "";
}

webrtc.connection.on("message", function(data) {
    if (data.type === "chat") {
        // message, table, sent?
        addMessageToTable(data.payload.message, document.getElementById("message-table"), false);
    }
});