var socket = io();


socket.emit('chat message', "hello i love you");

const root_div = document.querySelector(".root_div");


root_div.innerHTML = '<p>Hello</p>';

alert("!!!")

root_div.innerHTML = '<h>???</h>';