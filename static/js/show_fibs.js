$(function() {
    var conn;
    var log = $('#ws-log');

    function appendLog(msg) {
        var d = log[0];
        msg.appendTo(log);
        console.log(msg);
    }

    if ("WebSocket" in window) {
        conn = new WebSocket("ws://localhost:8080/ws");
        console.log(conn);
        conn.onopen = function(evt) {
            $('#ws-img').attr("src", "/static/img/ws-green.png"); // XXX: make it a matter of setting a class on the img
            $('#ws-conn').text("Connected!");
        };
        conn.onclose = function(evt) {
            appendLog($("<div><b>Connection closed.</b></div>"));
            $('#ws-img').attr("src", "/static/img/ws-red.png"); // XXX: make it a matter of setting a class on the img
            $('#ws-conn').text('No connection');
        };
        conn.onmessage = function(evt) {
            appendLog($("<div/>").text(evt.data));
        };
    } else {
        appendLog($("<div><b>Your browser does not support WebSockets.</b></div>"));
    }
});
