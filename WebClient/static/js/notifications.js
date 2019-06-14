function createWebSocket(address, name) {
    socket = new WebSocket(address);
    socketName = name;

    socket.onopen = function() {
        console.log("Connection is openned");
        var cameras = [{'serial': 'aeiou12345', 'url_cam': 'video.mp4'}]
        socket.send(JSON.stringify({'type': 'START',
            'cameras': cameras}));
    }
    socket.onmessage = function(e) {
        j = JSON.parse(e.data);

        // msg = {'type': 'FRAMES', 'status': 'OK', 
        // 'data': str(data), 'camera': self.camera}

        if (j.type == "FRAMES" && j.status == "OK") {

            var sframe = j.data;
            var cam_id = j.camera;
            var src = 'data:image/jpg;base64,' + sframe;
            var image = document.getElementById(cam_id);

            image.src = "";
            image.src = src;

            socket.send(JSON.stringify({'type': 'GET', 
                'camera': cam_id
            }));
        }
        else if(j.type == "FRAMES" && j.status == "EMPTY") {
            socket.send(JSON.stringify({'type': 'GET',
                'data': 'video_1.mp4'}));
        }
    }
    socket.onerror = function(e) {
        console.log("Error creating Websocket connection to " + address);
        console.log(e);
    }
    socket.onclose = function(e) {
        if (e.target == socket) {
            console.log("Disconnect.");
        }
    }
}