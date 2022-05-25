""" Мультиагентные среды для игры в дурака """


# %% imports 
from enum import Enum, auto

import numpy as np
from gym.core import Env
from transitions import Machine


# %% constants
class SUIT(Enum):
    """ Масти карт """
    SPADES = auto()
    HEARTS = auto()
    CLUBS = auto()
    DIAMONDS = auto()


class TURN_TYPE(Enum):
    """ Типы хода """
    START = auto()
    """ Атака на первом ходу """
    ATTACK = auto()
    """ Ходит на... """
    DEFENSE = auto()
    """ Отбивается """
    ATTACK_END = auto()
    """ Дает карты в догонку """
    DEFENSE_END = auto()
    """ Не может побиться, берет карты """
    WIN = auto()
    """ Выиграл игру """
    LOSE = auto()
    """ Проиграл игру """


class ACTION_TYPE(Enum):
    """ Типы действий """
    PUT = auto()
    """ Положить карту или побиться картой """
    TAKE = auto()
    """ Взять карты после неудачной попытки отбиться """
    FINISH = auto()
    """ Закончить давать карты """


MIN_PLAYER_CARDS = 6
""" Минимальное число карт у игрока на руке """
MAX_CARDS_NUMBER_BEFORE_FIRST_BEAT = 5
""" Первый отбой 5 карт """
ZERO_CARDS = 0
""" У игрока осталось 0 карт на руке"""
FULL_DECK_SIZE = 36
""" Размер полной колоды"""
FIRST_PLAYER_INDEX = 0
""" Номер первого игрока """
SECOND_PLAYER_INDEX = 1
""" Номер второго игрока """

class UnknownTransitionError(Exception):
    pass


# %% classes
class Turn_2a_v3:
    _transitions = [
        (ACTION_TYPE.PUT.name, TURN_TYPE.START,TURN_TYPE.DEFENSE, True),
        (ACTION_TYPE.PUT.name, TURN_TYPE.ATTACK, TURN_TYPE.DEFENSE, True),
        (ACTION_TYPE.PUT.name, TURN_TYPE.DEFENSE, TURN_TYPE.ATTACK, True),
        (ACTION_TYPE.PUT.name, TURN_TYPE.ATTACK_END, TURN_TYPE.ATTACK_END, False),
        (ACTION_TYPE.TAKE.name, TURN_TYPE.DEFENSE, TURN_TYPE.ATTACK_END, True),
        (ACTION_TYPE.FINISH.name, TURN_TYPE.ATTACK, TURN_TYPE.START, True),
        (ACTION_TYPE.FINISH.name, TURN_TYPE.ATTACK_END, TURN_TYPE.START, False)
    ]
    """ action, state, new_state, swap_or_not """

    def __init__(self):
        self._machine = Machine(
            model=self,
            states=TURN_TYPE,
            initial=TURN_TYPE.START,
            transitions=self._tuples_transitions_to_dicts()
        )
        self.reset()

    def _tuples_transitions_to_dicts(self):
        """ Приводит tuples к dicts """
        res = list()
        for elem in self._transitions:
            d = self._tuple_to_dict(elem)
            res.append(d)
        return res

    def _tuple_to_dict(self, tup):
        d = {
            'trigger': tup[0],
            'source': tup[1],
            'dest': tup[2],
        }
        if tup[3]:  # Если нужно вызывать метод swap
            d['before'] = 'swap'
        return d

    def reset(self):
        self._player = FIRST_PLAYER_INDEX
        """ Ходящий игрок """
        self.state = TURN_TYPE.START
        """ Состояние ходящего игрока"""
        self._player_cards = [MIN_PLAYER_CARDS, MIN_PLAYER_CARDS]
        """ Число карт у игроков на руках"""
        self._first_beat = True
        """ Первый отбой """


    def swap(self):
        """ Смена хода.
        Меняет поля, отслеживающие, кто ходит. """
        self._player = int(not self._player)
    
    def turn(self, action_type: ACTION_TYPE):
        """ Выполнение хода, переход в новое состояние """
        self.trigger(action_type.name)


class Durak_2a_v0:
    """ Среда для игры в Дурака вдвоем
    
    Игроки ходят по очереди.
    """

    def __init__(self):
        pass

    def reset(self):
        pass
    
    def step(self, a):
        pass


# %%
if __name__ == '__main__':
    pass