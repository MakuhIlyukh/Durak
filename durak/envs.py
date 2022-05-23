'''Мультиагентные среды для игры в дурака'''


# %% imports 
from enum import Enum, auto

import numpy as np
from gym.core import Env


# %% constants
class SUIT(Enum):
    '''Масти карт'''
    SPADES = auto()
    HEARTS = auto()
    CLUBS = auto()
    DIAMONDS = auto()


class TURN_TYPE(Enum):
    '''Типы хода'''
    ATTACK = auto()
    '''Ходит на...'''
    DEFENSE = auto()
    '''Отбивается'''
    ATTACK_END = auto()
    '''Дает карты в догонку'''
    DEFENSE_END = auto()
    '''Не может побиться, берет карты'''


class ACTION_TYPE(Enum):
    '''Типы действий'''
    PUT = auto()
    '''Положить карту или побиться картой'''
    TAKE = auto()
    '''Взять карты после неудачной попытки отбиться'''
    FINISH = auto()
    '''Закончить давать карты'''


class Turn_2a:
    '''Отслеживает, чей сейчас ход и какой тип хода.
    
    .. warning:: Не проверяет корректность действий игроков!'''
    def __init__(self):
        self.reset()
    
    def reset(self):
        '''Начинает всегда первый игрок'''
        self._turn = [TURN_TYPE.ATTACK, TURN_TYPE.DEFENSE]
        self._player = 0
        self._other_player = 1
    
    def swap(self):
        '''Меняет поля, отслеживающие, кто ходит'''
        self._player, self._other_player = self._other_player, self._player

    def new_round(self, swap: bool=False):
        '''Начинает новый раунд
        
        :param swap: нужно ли менять атакующего
        '''
        if swap:
            self.swap()
        self._turn[self._player] = TURN_TYPE.ATTACK
        self._turn[self._other_player] = TURN_TYPE.DEFENSE

    def turn(self, action_type: ACTION_TYPE):
        '''Переход в новое состояние'''
        # Если атакующий кладет новую карту:
        if action_type is ACTION_TYPE.PUT:
            self.swap()
        # Если защищающийся, не может побиться и берет
        elif action_type is ACTION_TYPE.TAKE:
            self._turn[self._player] = TURN_TYPE.DEFENSE_END
            self._turn[self._other_player] = TURN_TYPE.ATTACK_END
            self.swap() 
        # Если атакующий заканчивает подкидывать карты
        elif action_type is ACTION_TYPE.FINISH:
            # Если отбивающийся не смог побиться
            if self._turn[self._other_player] is TURN_TYPE.DEFENSE_END:
                self.new_round(swap=False)
            # Если отбивающийся смог побиться
            else:
                self.new_round(swap=True)
    
    def reverse_and_swap(self):
        '''Меняет состояния игроков
        и поля, отслеживающие, кто ходит.'''
        self._turn.reverse()
        self.swap()





# %% classes
class Durak_2a_v0:
    '''Среда для игры в Дурака вдвоем
    
    Игроки ходят по очереди.
    '''

    def __init__(self):
        pass

    def reset(self):
        pass
    
    def step(self, a):
        pass


# %%
if __name__ == '__main__':
    pass