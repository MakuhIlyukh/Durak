""" ? """


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask(__name__)
app.config['SECRET_KEY'] = 'THIS IS VERY SECRET KEY!'
sio = SocketIO(app)


@app.route('/')
def index():
    # maybe render_template is redudant
    # TODO: find method for static html (not template)
    return render_template("index.html")


@sio.event
def connect(auth):
    print(f"{request.sid} connected.")


@sio.event
def disconnect():
    print(f"{request.sid} disconected.")


@sio.on('chat message')
def chat_message(data):
    print(f"message was recieved: {data}")


if __name__ == '__main__':
    sio.run(app, debug=True)