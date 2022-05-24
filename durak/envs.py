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


class ACTION_TYPE(Enum):
    """ Типы действий """
    PUT = auto()
    """ Положить карту или побиться картой """
    TAKE = auto()
    """ Взять карты после неудачной попытки отбиться """
    FINISH = auto()
    """ Закончить давать карты """


class UnknownTransitionError(Exception):
    pass


# %% classes
class Turn_2a:
    """ Отслеживает, чей сейчас ход и какой тип хода.
    
    .. warning:: Не проверяет корректность действий игроков! """
    def __init__(self):
        self.reset()
    
    def reset(self):
        """ Начинает всегда первый игрок """
        self.state = [TURN_TYPE.ATTACK, TURN_TYPE.DEFENSE]
        self._player = 0
        self._other_player = 1
    
    def swap(self):
        """ Смена хода
        Меняет поля, отслеживающие, кто ходит """
        self._player, self._other_player = self._other_player, self._player

    def new_round(self, swap: bool=False):
        """ Начинает новый раунд
        
        :param swap: нужно ли менять атакующего
        """
        if swap:
            self.swap()
        self.state[self._player] = TURN_TYPE.ATTACK
        self.state[self._other_player] = TURN_TYPE.DEFENSE

    def turn(self, action_type: ACTION_TYPE):
        """ Переход в новое состояние """
        # Если атакующий кладет новую карту:
        if action_type is ACTION_TYPE.PUT:
            self.swap()
        # Если защищающийся, не может побиться и берет
        elif action_type is ACTION_TYPE.TAKE:
            self.state[self._player] = TURN_TYPE.DEFENSE_END
            self.state[self._other_player] = TURN_TYPE.ATTACK_END
            self.swap() 
        # Если атакующий заканчивает подкидывать карты
        elif action_type is ACTION_TYPE.FINISH:
            # Если отбивающийся не смог побиться
            if self.state[self._other_player] is TURN_TYPE.DEFENSE_END:
                self.new_round(swap=False)
            # Если отбивающийся смог побиться
            else:
                self.new_round(swap=True)
    
    def reverse_and_swap(self):
        """ Меняет состояния игроков
        и делает смену хода. """
        self.state.reverse()
        self.swap()


class Turn_2a_v1:
    """ Отслеживает, чей сейчас ход и какой тип хода.
    
    .. warning:: Не проверяет корректность действий игроков! """
    
    _transitions = [
        (ACTION_TYPE.PUT, TURN_TYPE.START, TURN_TYPE.DEFENSE, True),
        (ACTION_TYPE.PUT, TURN_TYPE.ATTACK, TURN_TYPE.DEFENSE, True),
        (ACTION_TYPE.PUT, TURN_TYPE.DEFENSE, TURN_TYPE.ATTACK, True),
        (ACTION_TYPE.PUT, TURN_TYPE.ATTACK_END, TURN_TYPE.ATTACK_END, False),
        (ACTION_TYPE.TAKE, TURN_TYPE.DEFENSE, TURN_TYPE.ATTACK_END, True),
        (ACTION_TYPE.FINISH, TURN_TYPE.ATTACK, TURN_TYPE.START, True),
        (ACTION_TYPE.FINISH, TURN_TYPE.ATTACK_END, TURN_TYPE.START, False)
    ]
    """ action, state, new_state, swap_or_not """

    def __init__(self):
        self.reset()
    
    def reset(self):
        """ Начинает всегда первый игрок """
        self._player = 0
        self.state = TURN_TYPE.START
    
    def swap(self):
        """ Смена хода
        Меняет поля, отслеживающие, кто ходит """
        self._player = int(not self._player)

    def new_round(self, swap: bool=False):
        """ Начинает новый раунд
        
        :param swap: нужно ли менять атакующего
        """
        self.change(TURN_TYPE.START, swap)

    def _change(self, new_turn: TURN_TYPE, swap: bool=False):
        """ Переходит в новое состояние.
        
        :param swap: нужно ли менять атакующего
        """
        if swap:
            self.swap()
        self.state = new_turn

    def turn(self, action_type: ACTION_TYPE):
        """ Выполнение хода, переход в новое состояние """
        for trans_action_type, source, dest, swap in self._transitions:
            if (action_type is trans_action_type and self.state is source):
                self._change(dest, swap)
                return
        
        raise UnknownTransitionError(
            f"Unknown action <{action_type}> for turn <{self.state}>")


class Turn_2a_v2:
    _transitions = [
        (ACTION_TYPE.PUT.name, TURN_TYPE.START, TURN_TYPE.DEFENSE, True),
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
        """ Приводит tuple к диктам """
        res = list()
        for elem in self._transitions:
            d = {
                'trigger': elem[0],
                'source': elem[1],
                'dest': elem[2],
            }
            if elem[3]:  # Если нужно вызывать метод swap
                d['before'] = 'swap'
            res.append(d)
        return res

    def reset(self):
        self._player = 0
        self.state = TURN_TYPE.START

    def swap(self):
        """ Смена хода
        Меняет поля, отслеживающие, кто ходит. """
        self._player = int(not self._player)
    
    def turn(self, action_type: ACTION_TYPE):
        """ Выполнение хода, переход в новое состояние """
        self.trigger(action_type.name)
    

class Turn_2a_v3:
    pass


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