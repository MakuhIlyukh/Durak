""" Пример использования Flask вместе с socketio"""


from flask import Flask
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'THIS IS VERY SECRET KEY!'
sio = SocketIO(app)


@app.route('/')
def index():
    return "Response :)"


@sio.event
def connect(sid, environ):
    print(f"{sid=} connected.")


@sio.event
def disconnect(sid, environ):
    print(f"{sid=} disconected.")


if __name__ == '__main__':
    sio.run(app)