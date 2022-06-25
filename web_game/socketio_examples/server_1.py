""" Пример aiohttp-сервера c socket.io .

"""


from aiohttp import web 
from socketio import AsyncServer, WSGIApp


# create a Socket.IO AsyncServer
sio = AsyncServer(async_mode='aiohttp')
# attach to aiohttp app
app = web.Application()
sio.attach(app)


@sio.event
def connect(sid, environ):
    print(f"{sid=} connected.")


@sio.event
def disconnect(sid, environ):
    print(f"{sid=} disconected.")


async def hello(request):
    return web.Response(text="Hello, ILIA MAKUKHA")


app.add_routes([web.get('/', hello)])


if __name__ == '__main__':
    web.run_app(app)
