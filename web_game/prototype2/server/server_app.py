""" ? """

import logging

from flask import Flask, render_template, request, send_from_directory
from flask_socketio import (
    SocketIO, emit, join_room, leave_room, rooms)
from transitions import MachineError

from utils import Registry, Room
from utils import FullRoomExc, RoomNotFoundExc
from durak.envs.durak_2a_v0.envs import Durak_2a_v0
from durak.envs.durak_2a_v0.action import ACTION_TYPE
from durak.envs.durak_2a_v0.card import RANK, RANKS_MAPPING, SUIT, Card
from durak.envs.durak_2a_v0.states import TURN_TYPE


app = Flask(__name__, static_url_path='', static_folder='../client/build')
# TODO: remember to set the key
app.config['SECRET_KEY'] = 'THIS IS VERY SECRET KEY!'
# ???: Что за cors_allowed_origins?
# NOTE: без асинхронщины (async_handlers=False)
sio = SocketIO(app, cors_allowed_origins="*", async_handlers=False)

# disabling stupid get-post logging
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.ERROR)

registry = Registry()


def gen_info_message(env, i):
    """ Генерирует info сообщение для игрока"""
    if env.state is TURN_TYPE.ATTACK and env._player == i:
        return "Ваша атака"
    elif env.state is TURN_TYPE.ATTACK and env._other_player == i:
        return "Ожидание атакующей карты соперника"
    elif env.state is TURN_TYPE.DEFENSE and env._player == i:
        return "Ваша защита"
    elif env.state is TURN_TYPE.DEFENSE and env._other_player == i:
        return "Ожидание защищающей карты соперника"
    elif env.state is TURN_TYPE.SUCC_ATTACK and env._player == i:
        return "Даете карты в догонку"
    elif env.state is TURN_TYPE.SUCC_ATTACK and env._other_player == i:
        return "Берете карты в догонку"
    elif env.state is TURN_TYPE.START_ATTACK and env._player == i:
        return "Начало вашей атаки"
    elif env.state is TURN_TYPE.START_ATTACK and env._other_player == i:
        return "Начало атаки врага"
    elif env.state is TURN_TYPE.DRAW:
        return "Ничья"
    elif env.state is TURN_TYPE.WIN and env._player == i:
        return "Победа"
    elif env.state is TURN_TYPE.WIN and env._other_player == i:
        return "Проигрыш"
    elif env.state is TURN_TYPE.LOSS and env._player == i:
        return "Проигрыш"
    elif env.state is TURN_TYPE.LOSS and env._other_player == i:
        return "Победа"
    else:
        return "Unkown situation"


@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')


@sio.event
def connect(auth):
    app.logger.info(f"{request.sid} connected.")
    registry.register_user(request.sid)


@sio.event
def disconnect():
    print(f"{request.sid} disconected.")


@sio.on('chat message')
def chat_message(data):
    app.logger.info(f"message was recieved: {data}")


@sio.on('create room')
def create_room():
    room = Room()
    registry.register_room(room)
    registry.join_room(room.name, request.sid)
    room.set_host(request.sid)

    return {
        "status": "ok",
        "room_id": room.name
    }


@sio.on('join to room')
def join_to_room(data):
    try:
        room_id = data['room_id']
    except KeyError:
        return {
            "status": "bad",
            "message": "invalid room_id"
        }

    try:
        registry.join_room(room_id, request.sid)

        return {
            "status": "ok",
            "room_id": 123
        }
    except RoomNotFoundExc:
        return {
            "status": "bad",
            "message": "room not found"
        }
    except FullRoomExc:
        return {
            "status": "bad",
            "message": "room is full"
        }


@sio.on('ready to play')
def ready_to_play(data):
    app.logger.info(f"{request.sid} ready to play!")

    try:
        room_id = data['room_id']
    except KeyError:
        return {
            "status": "bad",
            "message": "invalid room_id"
        }

    try:
        room = registry.get_room(room_id)
    except RoomNotFoundExc:
        return {
            "status": "bad",
            "message": "room not found"
        }

    sid = request.sid
    if not room.contains(sid):
        return {
            "status": "bad",
            "message": "user not in room"
        }
    
    room.user_by_sid(sid).is_ready = True
    if not (room.is_all_ready() and room.is_full()):
        return {
            "status": "ok",
        }
    elif not room.game_started:
        room.game_started = True
        env = Durak_2a_v0()
        room.set_env(env)
        for i, u in enumerate(room.users):    
            sio.emit(
                'game state',
                {
                    "playerCardsResp": [{"rank": card.rank.__str__(),
                                         "suit": card.suit.__str__()}
                                        for card in room.env._cards[i]],
                    "playerTableResp": [{"rank": card.rank.__str__(),
                                         "suit": card.suit.__str__()}
                                        for card in room.env._table[i]],
                    "enemyTableResp": [{"rank": card.rank.__str__(),
                                         "suit": card.suit.__str__()}
                                        for card in room.env._table[1 - i]],
                    "enemyCardsResp": len(room.env._cards[1 - i]),
                    "trumpCardResp": {
                        "rank": room.env._trump_card.rank.__str__(),
                        "suit": room.env._trump_card.suit.__str__()
                    },
                    "deckSizeResp": len(room.env._deck),
                    "infoMesResp": gen_info_message(room.env, i),
                },
                to=u.sid,
            )
    else:
        return {
            "status": "ok"
        }


@sio.on("step")
def step(data):
    # action parsing
    action = data['action']
    if action == 'PUT':
        action = ACTION_TYPE.PUT
    elif action == 'FINISH':
        action = ACTION_TYPE.FINISH
    else:
        return {
            "status": "bad",
            "message": "unknown action"
        }
    
    # TODO: Хорош хардкодить!
    rank = data['rank']
    if rank is None:
        pass
    elif rank == '6':
        rank = RANK.SIX
    elif rank == '7':
        rank = RANK.SEVEN
    elif rank == '8':
        rank = RANK.EIGHT
    elif rank == '9':
        rank = RANK.NINE
    elif rank == '10':
        rank = RANK.TEN
    elif rank == 'J':
        rank = RANK.JACK
    elif rank == 'Q':
        rank = RANK.QUEEN
    elif rank == 'K':
        rank = RANK.KING
    elif rank == 'A':
        rank = RANK.ACE
    else:
        return {
            "status": "bad",
            "message": "unknown card rank"
        }
    
    suit = data['suit']
    if suit is None:
        pass
    elif suit == '♠':
        suit = SUIT.SPADES
    elif suit == '♣':
        suit = SUIT.CLUBS
    elif suit == '♥':
        suit = SUIT.HEARTS
    elif suit == '♦':
        suit = SUIT.DIAMONDS
    else:
        return {
            "status": "bad",
            "message": "unknown card suit"
        }
    
    card = Card(rank=rank, suit=suit)

    # room_id parsing and checking
    try:
        room_id = data['room_id']
    except KeyError:
        return {
            "status": "bad",
            "message": "invalid room_id"
        }

    try:
        room = registry.get_room(room_id)
    except RoomNotFoundExc:
        return {
            "status": "bad",
            "message": "room not found"
        }

    sid = request.sid
    if not room.contains(sid):
        return {
            "status": "bad",
            "message": "user not in room"
        }
    
    if not room.game_started:
        return {
            "status": "bad",
            "message": "users aren't ready"
        }

    if room.users[room.env._player].sid != sid:
        return {
            "status": "bad",
            "message": "not your turn"
        }

    if action is ACTION_TYPE.FINISH:
        card = None  
    try:
        if room.env.trigger(action.name, card):
            for i, u in enumerate(room.users):    
                sio.emit(
                    'game state',
                    {
                        "playerCardsResp": [{"rank": card.rank.__str__(),
                                            "suit": card.suit.__str__()}
                                            for card in room.env._cards[i]],
                        "playerTableResp": [{"rank": card.rank.__str__(),
                                            "suit": card.suit.__str__()}
                                            for card in room.env._table[i]],
                        "enemyTableResp": [{"rank": card.rank.__str__(),
                                            "suit": card.suit.__str__()}
                                            for card in room.env._table[1 - i]],
                        "enemyCardsResp": len(room.env._cards[1 - i]),
                        "trumpCardResp": {
                            "rank": room.env._trump_card.rank.__str__(),
                            "suit": room.env._trump_card.suit.__str__()
                        },
                        "deckSizeResp": len(room.env._deck),
                        "infoMesResp": gen_info_message(room.env, i),
                    },
                    to=u.sid,
                )
        else:
            return {
                "status": "bad",
                "message": "bad action or card"
            }
    except MachineError:
        return {
            "status": "bad",
            "message": "bad action or card"
        }


if __name__ == '__main__':
    sio.run(app, debug=True)  # Debug=True! Not for production!