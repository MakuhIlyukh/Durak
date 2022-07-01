""" ? """


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
app.config['SECRET_KEY'] = 'THIS IS VERY SECRET KEY!'
sio = SocketIO(app, cors_allowed_origins="*")


@sio.event
def connect(auth):
    print(f"{request.sid} connected.")


@sio.event
def disconnect():
    print(f"{request.sid} disconected.")


@sio.on('chat message')
def chat_message(data):
    print(f"message was recieved: {data}")


@sio.on('create room')
def create_room():
    return {
        "status": "ok",
        "room_id": 123
    }


@sio.on('join to room')
def join_to_room(data):
    return {
        "status": "ok",
        "room_id": 123
    }


if __name__ == '__main__':
    sio.run(app, debug=True)  # Debug=True! Not for production!