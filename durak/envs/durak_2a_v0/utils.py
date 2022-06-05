""" Вспомогательные функции """


from enum import Enum
from typing import Optional, List

import numpy as np

from durak.envs.durak_2a_v0.card import Card, RANK, FULL_DECK_SIZE


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
