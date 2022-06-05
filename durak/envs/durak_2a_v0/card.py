""" Классы для игральных карт """


from enum import Enum
from dataclasses import dataclass


# Константы для обозначения результатов сравнения двух карт
NOT_COMPARABLE = -2
LESS = -1
EQUAL = 0
BIGGER = 1


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


FULL_DECK_SIZE = len(FULL_DECK)


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
