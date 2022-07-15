""" Вспомогательные функции """


from enum import Enum
from typing import Optional, List

import numpy as np

from durak.envs.durak_2a_v0.card import Card, RANK, FULL_DECK_SIZE, SUIT
from durak.envs.durak_2a_v0.action import ACTION_TYPE


ACTIONS_WITH_CARDS_NUM = FULL_DECK_SIZE + 1
""" Число всех возможных действий  """


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


def one_hot_action_and_card(action: ACTION_TYPE, card: Optional[Card]):
    oh = np.zeros(ACTIONS_WITH_CARDS_NUM)
    oh[0] = action.value
    if card is not None:
        # Первый бит уделяется под действие, поэтому мы смещаем на 1
        oh[card_ind(card) + 1] = 1  # + 1 IS IMPORTANT!
    return oh


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


# -----------------------------------------------
# Masks
# -----------------------------------------------
def create_empty_mask():
    """ Создает пустую маску для действий и карт """
    return np.zeros(ACTIONS_WITH_CARDS_NUM)


def mark_FINISH_on_mask(mask: np.array):
    """ Помечает FINISH на маске """
    mask[0] = 1


def mark_card_on_mask(mask: np.array,
                      card: Optional[Card]):
    """ Помечает карту на маске """
    if card is not None:
        # Первый бит уделяется под действие, поэтому мы смещаем на 1
        mask[card_ind(card) + 1] = 1  # + 1 IS IMPORTANT!


#------------------------------------------------
# for rlcard functions
#------------------------------------------------
def action_card_id(action: ACTION_TYPE, card: Optional[Card]):
    """ Возвращает id для пары (действие, карта)
    
    :param card: не может быть равен None, если action is PUT
    """
    if action is ACTION_TYPE.FINISH:
        return 0
    else:
        return 1 + card_ind(card)


def action_card_str(action: ACTION_TYPE, card: Optional[Card]):
    """ Возвращает строковое представление для пары (действие, карта).
    
    :param card: не может быть равен None, если action is PUT
    """
    if action is ACTION_TYPE.FINISH:
        return "f"
    else:
        return "p-" + card.__repr__()


def action_card_str_from_id(act_car_id: int):
    """ Возвращает строковое представление для пары (действие, карта) из id """
    if act_car_id == 0:
        return "f"
    else:
        return "p-" + card_from_ind(act_car_id - 1).__repr__()


def action_card_pair_from_str(act_car: str):
    """ Возвращает пару из строкового представления (действие, карты). """
    if act_car == "f":
        return (ACTION_TYPE.FINISH, None)
    else:
        return (ACTION_TYPE.PUT, Card.from_repr(act_car[2:]))


def action_card_id_from_str(act_car: str):
    """ Возвращает id строкового представления пары (действие, карты). """
    if act_car == "f":
        return 0
    else:
        return 1 + card_ind(Card.from_repr(act_car[2:]))