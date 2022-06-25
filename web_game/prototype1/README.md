# python-socketio instead flask-socketio
These two wrappers can also act as middlewares, forwarding any traffic that is not intended to the Socket.IO server to another application. This allows Socket.IO servers to integrate easily into existing WSGI or ASGI applications:
```
from wsgi import app  # a Flask, Django, etc. application
app = socketio.WSGIApp(sio, app)
```

# Сценарий использования

## Начало
При подключении показывать страницу с:
1. кнопкой "создать комнату";
2. форму ввода с кнопкой "подключиться к уже существующей".

### Нажатие на кнопку создать комнату:
Загружается страница с:
1. С отображением кода комнаты;
2. С текстом "ожидание игрока".

При присоединении в комнату второго:
1. Загружать страницу с игрой.

### Нажатие на кнопку присоединиться к комнате
1. Если комната существует(наверное, хост не отключился): загружать страницу с игрой;
2. Иначе загружать начальную страницу.

## Игра
Некоторые детали поведения:
- Если один из игроков отключился(iosocket disconnect):
    - оповестить оставшегося игрока;
    - удалить комнату;
    - загрузить начальную страницу.
- В конце:
    - оповестить, кто победил;
    - начать новую игру.