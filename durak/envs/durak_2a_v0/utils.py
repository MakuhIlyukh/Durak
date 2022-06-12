""" Вспомогательные функции """


from enum import Enum
from typing import Optional, List

import numpy as np

from durak.envs.durak_2a_v0.card import Card, RANK, FULL_DECK_SIZE, SUIT
from durak.envs.durak_2a_v0.action import ACTION_TYPE


# ===============================================
# one-hot-encodings
# ===============================================
def one_hot_enum(enum_member: Enum):
    """ One hot encoding for any enumeration member """
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
    # ???: Может лучше, чтобы для None был отдельный бит?
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


# -----------------------------------------------
# BAD CODE (Много магических констант, зависим от ACTION_TYPE)
# -----------------------------------------------
def create_empty_actcar_oh():
    """ Создает пустой one hot encoding для действия и карты """
    return np.zeros(1 + FULL_DECK_SIZE)  # ???: MAGIC CONSTANT


def mark_FINISH_actcar_onehot(oh: np.array):
    """ Помечает FINISH на onehot encoding'е для действия и карты """
    oh[0] = 1  # ???: MAGIC CONSTANT


def mark_card_actcar_onehot(oh: np.array,
                            card: Optional[Card]):
    """ Помечает карту на onehot encoding'е для действия и карты """
    if card is not None:
        # Первый бит уделяется под действие, поэтому мы смещаем на 1
        # ???: MAGIC CONSTANT
        oh[card_ind(card) + 1] = 1  # + 1 IS IMPORTANT!
# -----------------------------------------------
# END OF BAD CODE
# -----------------------------------------------


# ===============================================
# one-hot-decodings
# ===============================================
def card_from_ind(ind: int):
    """ Обратная функция к card_ind """
    return Card(rank=RANK(ind % len(RANK)),
                suit=SUIT(ind // len(RANK)))


# TODO: скользкий момент с обработкой None-случая
#       возможно стоит как-то изменить
def card_ind_from_one_hot(oh: np.array):
    """ Возвращает индекс карты из one-hot-encoding.

    :param oh: np.array с длиной равной размеру полной колоды.
        В этот массив входит ТОЛЬКО one-hot-encoding карты!

    НЕ ДЕЛАЕТ ПРОВЕРКУ НА ТО, ЧТО `oh` НЕ РАВЕН НУЛЮ!
    """
    return np.argmax(oh)


def card_from_one_hot(oh: np.array):
    """ Обратная функция к one_hot_card """
    if (oh == 0).all():
        return None
    else:
        return card_from_ind(card_ind_from_one_hot(oh))


def action_and_card_from_one_hot(oh: np.array):
    """ Обратная функция к one_hot_action_and_card """
    action = ACTION_TYPE(oh[0])
    card = card_from_one_hot(oh[1:])
    return action, card


def card_list_from_one_hot(oh: np.array):
    """ Обратная функция к one_hot_card_list """
    res = []
    for ind in oh.nonzero()[0]:
        res.append(card_from_ind(ind))
    return res
