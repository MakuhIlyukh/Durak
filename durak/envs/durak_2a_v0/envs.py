""" Мультиагентные среды для игры в дурака """
# TODO: избавься от типизации везде или добавь ее
# TODO: pep8 codestyle check
# TODO: измени Card на Optional[Card] = None


# %% imports 
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, List

import numpy as np
from gym.core import Env
from transitions import Machine


MIN_PLAYER_CARDS = 6
""" Минимальное число карт у игрока на руке """
MAX_PAIRS_NUMBER_BEFORE_FIRST_BEAT = 5
""" Первый отбой 5 (пар) карт """
FULL_DECK_SIZE = 36
""" Размер полной колоды"""
FIRST_PLAYER_INDEX = 0
""" Номер первого игрока """
SECOND_PLAYER_INDEX = 1
""" Номер второго игрока """

# Константы для обозначения результатов сравнения двух карт
NOT_COMPARABLE = -2
LESS = -1
EQUAL = 0
BIGGER = 1

# НАГРАДЫ
LOSS_REWARD = -1
WIN_REWARD = 1
DRAW_REWARD = 0
INVALID_REWARD = -5


class RANK(Enum):
    """ Ранги карт """
    SIX = 0
    SEVEN = 1
    EIGHT = 2
    NINE = 3
    TEN = 4
    JACK = 5
    QUEEN = 6
    KING = 7
    ACE = 8 

    def __str__(self):
        return RANKS_MAPPING[self.value]


RANKS_MAPPING = ['6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
""" Нужен для реализация __str__ в классе RANK """


class SUIT(Enum):
    """ Масти карт """
    # ???: Возможно лучше на инты заменить
    #      и просто перегрузить __str__  и/или  __repr__
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3

    def __str__(self):
        return SUITS_MAPPING[self.value]      


SUITS_MAPPING = ['♠', '♡', '♣', '♢']
""" Нужен для реализация __str__ в классе SUIT """


class TURN_TYPE(Enum):
    """ Типы хода """
    START_ATTACK = 0
    """ Начинает атаковать """
    ATTACK = 1
    """ Ходит на... """
    DEFENSE = 2
    """ Отбивается """
    SUCC_ATTACK = 3
    """ Дает карты в догонку """
    WIN = 4
    """ Выиграл игру """
    LOSS = 5
    """ Проиграл игру """
    DRAW = 6
    """ Ничья """
    INVALID = 7
    """ Игрок совершил запрещенное действие """


class ACTION_TYPE(Enum):
    """ Типы действий """
    PUT = 0
    """ Положить карту или побиться картой """
    FINISH = 1
    """ Закончить давать карты / Закончить пытаться отбиваться """


class UnknownTransitionError(Exception):
    pass


@dataclass(frozen=True)
class Card:
    rank: RANK
    suit: SUIT

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"


FULL_DECK = [
    Card(rank, suit)
    for suit in SUIT
    for rank in RANK
]


# ===============================================
# Сравнения карт по правилам Дурака
# ===============================================
def less(card1: Card, card2: Card, trump: SUIT):
    if card1.suit is card2.suit:
        return card1.rank.value < card2.rank.value
    else:
        return card2.suit is trump


def equal(card1: Card, card2: Card, trump: SUIT):
    return card1.rank is card2.rank and card1.suit is card2.suit


def bigger(card1: Card, card2: Card, trump: SUIT):
    if card1.suit is card2.suit:
        return card1.rank.value > card2.rank.value
    else:
        return card1.suit is trump


def compare(card1: Card, card2: Card, trump: SUIT):
    if card1.suit is card2.suit:
        if card1.rank.value < card2.rank.value:
            return LESS
        elif card1.rank.value == card2.rank.value:
            return EQUAL
        else:
            return BIGGER
    else:
        if card2.suit is trump:
            return LESS
        elif card1.suit is trump:
            return BIGGER
        else:
            return NOT_COMPARABLE


# ===============================================
# one-hot-encodings
# ===============================================
def one_hot_enum(enum_member: Enum):
    """ One hot encoding for any enumeration member"""
    oh = np.zeros(len(enum_member.__class__))
    oh[enum_member.value] = 1
    return oh


def card_ind(card: Card):
    """ Возвращает индекс карты для one-hot-encoding'а """
    return card.suit.value*len(RANK) + card.rank.value


def one_hot_card(card: Optional[Card]):
    """ One hot encoding for card.
    :param card: если None, вернет массив из нулей 
    """
    oh = np.zeros(FULL_DECK_SIZE)
    if card is not None:
        oh[card_ind(card)] = 1
    return oh
    

def one_hot_card_list(cards: List[Card]):
    """ One hot encoding for list of cards """
    oh = np.zeros(FULL_DECK_SIZE)
    for c in cards:
        oh[card_ind(c)] = 1
    return oh
# ===============================================


# ???: Когда вызывать пополнение карт у игроков?
# ???: Как и когда проверять, что игра закончилась?
# ???: Как и когда проверять, что ход корректен?
# ???: В какой форме передавать действия в step
# ???: Как и когда проверять, что игрок еще может добавить карту?
# ???: Что насчет ничьей?
class Durak_2a_v0(Env):
    _transitions = [
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.DRAW,
            "before": [], # ???: Need to add anything? 
            "conditions": ["_put_start_attack_to_draw_cond"]
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.WIN,
            "before": [], # ???: Need to add anything? 
            "conditions": ["_put_start_attack_to_win_cond"]
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.LOSS,
            "before": [], # ???: Need to add anything? 
            "conditions": ["_put_start_attack_to_loss_cond"]
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.DEFENSE,
            "before": ["_put_callback", "_swap_callback"],
            "conditions": ["_put_start_attack_to_defense_cond"] 
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.DEFENSE,
            "dest": TURN_TYPE.ATTACK,
            "before": ["_put_callback", "_swap_callback"],
            "conditions": ["_put_defense_cond"] 
        },
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.DEFENSE,
            "dest": TURN_TYPE.SUCC_ATTACK,
            "before": ["_swap_callback"],
            # there is no conditions
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.ATTACK,
            "dest": TURN_TYPE.DEFENSE,
            "before": ["_put_callback", "_swap_callback"],
            "conditions": ["_put_attack_and_succ_attack_cond"] 
        },
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.ATTACK,
            "dest": TURN_TYPE.START_ATTACK,
            "before": ["_finish_attack_callback", "_swap_callback"],
            # there is no conditions 
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.SUCC_ATTACK,
            "dest": TURN_TYPE.SUCC_ATTACK,
            "before": ["_put_callback"],
            "conditions": ["_put_attack_and_succ_attack_cond"] 
        },
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.SUCC_ATTACK,
            "dest": TURN_TYPE.START_ATTACK,
            "before": ["_finish_succ_attack_callback"],
            # there is no conditions 
        },
    ]
    
    _num_of_players = 2
    """ Число игроков """

    def __init__(self, seed: Optional[int]=None):
        self._machine = Machine(
            model=self,
            states=TURN_TYPE,
            initial=TURN_TYPE.START_ATTACK,
            transitions=self._transitions
        )
        self.reset(seed)
    
    def reset(self, seed: Optional[int]=None):
        super().reset(seed=seed)
        self._player = FIRST_PLAYER_INDEX
        """ Ходящий игрок(поле будет меняться от хода к ходу) """
        self._other_player = SECOND_PLAYER_INDEX
        """ Не ходящий игрок """
        # Обновляем состояние ходящего игрока
        self._machine.set_state(TURN_TYPE.START_ATTACK)
        self._first_beat = True
        """ Первый отбой """
        self._deck = self._new_deck()
        """ Колода """
        self._cards = [[], []]
        """ Карты у игроков на руках """
        # Даем игрокам карты
        self._pop_cards_from_deck()
        self._beat = []
        """ Бито """
        self._table = [[], []]
        """ Карты по игрокам на столе """
        self._trump_card = self._deck[0]
        """ Козырная карта """
        self.rewards = [0, 0]
        """ Награды, полученные в конце игры """

    def _get_observation(self):
        """ Получить наблюдения для ходящего игрока """
        obs = []
        # setting state
        obs.append(one_hot_enum(self.state))
        # setting trump card
        obs.append(one_hot_card(self._trump_card))
        # setting player's hand
        obs.append(one_hot_card_list(self._cards[self._player]))
        # setting player's table
        obs.append(one_hot_card_list(self._table[self._player]))
        # setting other player's table
        obs.append(one_hot_card_list(self._table[self._other_player]))
        # setting last other player's table-card
        # if other player's table is empty then assigned array of zeros
        obs.append(one_hot_card(
            self._table[self._other_player][-1]
            if bool(self._table[self._other_player])
            else None
        ))  
        return np.concatenate(obs)


    def _step(self,
              action_type: ACTION_TYPE,
              card: Optional[Card]):
        """ Выполняет действие """
        # do action (or not if it's invalid)
        if not self.trigger(action_type.name, card):
            self.to_INVALID()
        raise NotImplementedError("Допиши :)")

    # ===========================================
    # enter callbacks
    # ===========================================
    def on_enter_WIN(self):
        self._set_rewards(WIN_REWARD, LOSS_REWARD)
    
    def on_enter_LOSS(self):
        self._set_rewards(LOSS_REWARD, WIN_REWARD)
    
    def on_enter_DRAW(self):
        self._set_rewards(DRAW_REWARD, DRAW_REWARD)
    
    def on_enter_INVALID(self):
        self._set_rewards(INVALID_REWARD, DRAW_REWARD)

    # ===========================================
    # transition conditions
    # ===========================================
    def _put_start_attack_to_defense_cond(self, card: Optional[Card]):
        """ В начале атаки можно положить карту, если: """
        return (
            # if card is None then card not in self._cards[...]
            card in self._cards[self._player]
            and
            bool(self._cards[self._other_player])  # TODO: maybe redudant
        )
    
    def _put_start_attack_to_draw_cond(self, card: Optional[Card]):
        """ Ничья если: """
        return (
            not bool(self._cards[self._player])
            and
            not bool(self._cards[self._other_player])
        )
    
    def _put_start_attack_to_win_cond(self, card: Optional[Card]):
        """ Победа текущего игрока, если: """
        return (
            not bool(self._cards[self._player])
            and
            bool(self._cards[self._other_player])  # TODO: maybe redudant
        )
    
    def _put_start_attack_to_loss_cond(self, card: Optional[Card]):
        """ Проигрыш текущего игрока, если: """
        return (
            bool(self._cards[self._player])  # TODO: maybe redudant
            and
            not bool(self._cards[self._other_player])
        )

    def _put_attack_and_succ_attack_cond(self, card: Optional[Card]):
        """ Атакующий может положить карту, если: 
        
        :param card: карта, которую хочет положить атакующий
        """
        # Предусловия:
        # attacking player: self._player
        # defending player: self._other_player
        return (
            # if card is None then card not in self._cards[...]
            card in self._cards[self._player]
            and 
            self._same_rank_on_table(card)
            and
            len(self._table[self._player])
              < self._acceptable_quantity(self._other_player)
        )
    
    def _put_defense_cond(self, card: Optional[Card]):
        """ Защищающийся может положить карту, если: 
        
        :param card: карта, которую хочет положить защищающийся
        """
        # Предусловия:
        # attacking player: self._other_player
        # defending player: self._player
        # Последняя карта, которую положил атакующий игрок на стол
        att_card = self._table[self._other_player][-1]
        return (
            # if card is None then card not in self._cards[...]
            card in self._cards[self._player]
            and
            less(att_card, card, self._trump_card.suit)
        )

    # ===========================================
    # transition callbacks
    # ===========================================
    def _put_callback(self, card: Card):
        self._table[self._player].append(card)
        # HACK: удаляет только первое вхождение
        self._cards[self._player].remove(card)
    
    def _finish_attack_callback(self, card: Card):
        # Пополняем бито
        self._beat.extend(self._table[self._player])
        self._beat.extend(self._table[self._other_player])
        self._first_beat = False
        # Очищаем стол
        self._clear_table()
        # Берем карты из колоды
        self._pop_cards_from_deck()

    def _finish_succ_attack_callback(self, card: Card):
        # Пополняем карты неудачно защитившегося игрока
        self._cards[self._other_player].extend(self._table[self._other_player])
        self._cards[self._other_player].extend(self._table[self._player])
        # Очищаем стол
        self._clear_table()
        # Берем карты из колоды
        self._pop_cards_from_deck()
    
    def _swap_callback(self, card: Optional[Card]):
        """ Смена хода.
        Меняет поля, отслеживающие, кто ходит. """
        self._player, self._other_player = self._other_player, self._player
    
    # ===========================================
    # support
    # ===========================================
    def _same_rank_on_table(self, card: Card):
        """ Проверяет, есть ли карты с таким рангом на столе. """
        return (card.rank in (elem.rank for elem in self._table[0])
                or card.rank in (elem.rank for elem in self._table[1]))
    
    def _acceptable_quantity(self, def_player: int):
        """ Допустимое количество карт. """
        return min(len(self._cards[def_player])
                   + len(self._table[def_player]),
                   5 if self._first_beat else 6)

    def _attacking_player(self):
        """ Возвращает атакующего игрока.
        Не работает для состояний win, loss, draw. """
        if self.state in (TURN_TYPE.ATTACK,
                          TURN_TYPE.START_ATTACK,
                          TURN_TYPE.SUCC_ATTACK):
            return self._player
        else:
            return self._other_player

    def _defending_player(self):
        """ Возвращает атакующего игрока.
        Не работает для состояний win, loss, draw. """
        if self.state in (TURN_TYPE.DEFENSE,):
            return self._player
        else:
            return self._other_player
    
    def _clear_table(self):
        self._table = [[], []]
    
    def _new_deck(self) -> List[Card]:
        """ Создает случайную колоду """
        res = FULL_DECK.copy()
        self.np_random.shuffle(res)
        return res

    def _pop_cards_from_deck(self):
        """ Пополняет карты игроков из колоды.
        
        Порядок получения карт, зависит от `self._player`,
        поэтому метод должен вызываться только в начале игры
        и в конце атаки до смены атакующего. """
        for i in (self._player, self._other_player):
            while (bool(self._deck)
                   and len(self._cards[i]) < MIN_PLAYER_CARDS):
                self._cards[i].append(self._deck.pop())
    
    def _set_rewards(self, player_reward, other_player_reward):
        """ Назначает награды """
        self.rewards[self._player] = player_reward
        self.rewards[self._other_player] = other_player_reward

# %%
if __name__ == '__main__':
    pass