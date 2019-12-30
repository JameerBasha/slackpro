$(document).ready(function () {
        var socket = io.connect();
        var groupidnumber = (document.getElementById('groupidnumber').innerText)
        var username = (document.getElementById('username').innerText)
        socket.on(String(groupidnumber), function (msg) {
            if (groupidnumber == msg['groupidnumber']) {
                $('#messagecontainer').prepend("<li><div class='collapsible-header'><img src='https://avatars.dicebear.com/v2/gridy/" + msg['username'] + ".svg' class='avatar-image'><span><b>" + msg['username'] + "</b></span> <br><span>" + msg['message'] + "</span></div> <div class='collapsible-body'><p>Sent : " + msg['time'] + "</p></div></li > ");
            }
            if (msg['username'] === (document.getElementById('username').innerText)) {
                document.getElementById('messageinputform').reset();
            }
            var messagecontainer = $('#messagecontainer');
            var child = messagecontainer.lastElementChild;
        });
        $('form#messageinputform').submit(function (event) {
            var timeToSend = String(new Date())
            if (document.getElementById('messageinputbox').value === '') {
                return false;
            }
            socket.emit('messagetoserver', {
                message: (document.getElementById('messageinputbox').value),
                username: (document.getElementById('username').innerText),
                groupidnumber: (document.getElementById('groupidnumber').innerText),
                time: timeToSend
            });
            return false;
        });
});
