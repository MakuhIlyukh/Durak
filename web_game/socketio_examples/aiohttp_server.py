from aiohttp import web


async def hello(request):
    return web.Response(text="Hello, ILIA MAKUKHA")


app = web.Application()
app.add_routes([web.get('/', hello)])


if __name__ == '__main__':
    web.run_app(app)