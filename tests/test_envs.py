import numpy as np
from transitions import MachineError
from tqdm import tqdm
import pytest
from copy import deepcopy

from durak.envs.durak_2a_v0.card import (
    Card, SUIT, RANK, FULL_DECK_SIZE, FULL_DECK)
from durak.envs.durak_2a_v0.utils import (
    ACTIONS_WITH_CARDS_NUM, action_and_card_from_one_hot, action_card_id, action_card_id_from_str, action_card_pair_from_str, action_card_str, card_from_one_hot, create_empty_mask,
    mark_card_on_mask, one_hot_card, mark_FINISH_on_mask,
    one_hot_enum, card_ind, one_hot_card_list, one_hot_action_and_card,
    card_from_ind, card_ind_from_one_hot, card_list_from_one_hot,
    create_empty_mask)
from durak.envs.durak_2a_v0.states import TURN_TYPE
from durak.envs.durak_2a_v0.action import ACTION_TYPE
from durak.envs.durak_2a_v0.envs import Durak_2a_v0


def test_action_type():
    assert len(ACTION_TYPE) == 2, "если action_type изменился, нужно переделать one-hot encoding в utils"
    assert ACTION_TYPE.PUT.value == 0
    assert ACTION_TYPE.FINISH.value == 1


def test__new_deck():
    env = Durak_2a_v0()
    deck_1 = env._new_deck()
    deck_2 = env._new_deck()
    assert deck_1 != deck_2  # probability is very small
    assert len(deck_1) == len(set(deck_1)) == 36 == len(SUIT)*len(RANK)
    assert set(deck_1) == set(deck_2) == set(FULL_DECK)


def test_full_deck():
    for suit in SUIT:
        for rank in RANK:
            assert Card(rank, suit) in FULL_DECK


def test_reset():
    env = Durak_2a_v0()
    env.reset()

    assert env._player == 0
    assert env._other_player == 1

    assert env._first_beat == True
    assert env._beat == []

    assert len(env._deck) == 36 - 6 - 6
    assert len(set(env._deck)) == len(env._deck) # все карты уникальны
    assert set(env._deck) | set(env._cards[0]) | set(env._cards[1]) == set(FULL_DECK)
    assert set(env._deck) & set(env._cards[0]) == set()
    assert set(env._deck) & set(env._cards[1]) == set()
    assert set(env._cards[0]) &  set(env._cards[1]) == set()

    assert env._table == [[], []]
    assert env.state is TURN_TYPE.START_ATTACK
    assert env.rewards == [0, 0]
    assert env.done == False

    env.reset()
    assert env._player == 0
    assert env._other_player == 1

    assert env._first_beat == True
    assert env._beat == []

    assert len(env._deck) == 36 - 6 - 6
    assert len(set(env._deck)) == len(env._deck) # все карты уникальны
    assert set(env._deck) | set(env._cards[0]) | set(env._cards[1]) == set(FULL_DECK)
    assert set(env._deck) & set(env._cards[0]) == set()
    assert set(env._deck) & set(env._cards[1]) == set()
    assert set(env._cards[0]) &  set(env._cards[1]) == set()

    assert env._table == [[], []]
    assert env.state is TURN_TYPE.START_ATTACK
    assert env.rewards == [0, 0]
    assert env.done == False


# FIXME: не хорошо покрывающий тест
def test__pop_cards_from_deck():
    env = Durak_2a_v0()
    env.reset()

    env._cards[0] = env._cards[0][0:3]
    env._cards[1] = env._cards[1][0:4]
    old_cards = deepcopy(env._cards)
    old_deck = deepcopy(env._deck)
    env._pop_cards_from_deck()

    assert env._cards[0] == old_cards[0] + old_deck[-3:][::-1]
    assert env._cards[1] == old_cards[1] + old_deck[-5:-3][::-1]
    assert env._deck == old_deck[:-5]


    env.reset()
    env._swap_callback(None)
    env._cards[1] = env._cards[1][0:3]
    env._cards[0] = env._cards[0][0:4]
    old_cards = deepcopy(env._cards)
    old_deck = deepcopy(env._deck)
    env._pop_cards_from_deck()

    assert env._cards[1] == old_cards[1] + old_deck[-3:][::-1]
    assert env._cards[0] == old_cards[0] + old_deck[-5:-3][::-1]
    assert env._deck == old_deck[:-5]


def test_card_ind():
    assert card_ind(Card(RANK.SIX, SUIT.HEARTS)) == 9
    assert card_ind(Card(RANK.SEVEN, SUIT.HEARTS)) == 10
    assert card_ind(Card(RANK.EIGHT, SUIT.HEARTS)) == 11
    assert card_ind(Card(RANK.NINE, SUIT.HEARTS)) == 12
    assert card_ind(Card(RANK.TEN, SUIT.HEARTS)) == 13
    assert card_ind(Card(RANK.JACK, SUIT.HEARTS)) == 14 
    assert card_ind(Card(RANK.QUEEN, SUIT.HEARTS)) == 15
    assert card_ind(Card(RANK.KING, SUIT.HEARTS)) == 16
    assert card_ind(Card(RANK.ACE, SUIT.HEARTS)) == 17

    k = 0
    for suit in SUIT:
        for rank in RANK:
            assert card_ind(Card(rank, suit)) == k
            k += 1


def test_card_from_ind():
    k = 0
    for suit in SUIT:
        for rank in RANK:
            card = Card(rank, suit)
            assert card_ind(card) == k
            assert card_from_ind(card_ind(card)) == card
            k += 1


def test_card_ind_from_one_hot():
    k = 0
    for suit in SUIT:
        for rank in RANK:
            card = Card(rank, suit)
            oh = one_hot_card(card)
            assert card_ind_from_one_hot(oh) == k
            k += 1


def test_card_from_one_hot():
    k = 0
    for suit in SUIT:
        for rank in RANK:
            card = Card(rank, suit)
            oh = one_hot_card(card)
            assert card_from_one_hot(oh) == card
            k += 1
    oh = one_hot_card(None)
    assert card_from_one_hot(oh) is None


def test_action_and_card_from_one_hot():
    for action in ACTION_TYPE:
        k = 0
        for suit in SUIT:
            for rank in RANK:
                card = Card(rank, suit)
                oh = one_hot_action_and_card(action, card)
                expected_oh = np.zeros(1 + FULL_DECK_SIZE)
                expected_oh[1 + k] = 1
                expected_oh[0] = action.value
                assert (oh == expected_oh).all()
                assert action_and_card_from_one_hot(oh) == (action, card)
                k += 1


def test_card_list_from_one_hot():
    M = 100
    for i in range(M):
        cards = np.random.choice(FULL_DECK, 6)
        expected = np.zeros(FULL_DECK_SIZE)
        for c in cards:
            expected[card_ind(c)] = 1
        oh = one_hot_card_list(cards)
        assert (oh == expected).all()
        assert (set(card_list_from_one_hot(oh)) == set(cards))


def test_one_hot_enum():
    assert (one_hot_enum(ACTION_TYPE.PUT) == [1, 0]).all()
    assert (one_hot_enum(ACTION_TYPE.FINISH) == [0, 1]).all()

    assert (one_hot_enum(ACTION_TYPE.PUT) == [1, 0]).all()
    assert (one_hot_enum(RANK.SIX) ==   [1, 0, 0, 0, 0, 0, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.SEVEN) == [0, 1, 0, 0, 0, 0, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.EIGHT) == [0, 0, 1, 0, 0, 0, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.NINE) ==  [0, 0, 0, 1, 0, 0, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.TEN) ==   [0, 0, 0, 0, 1, 0, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.JACK) ==  [0, 0, 0, 0, 0, 1, 0, 0, 0]).all()
    assert (one_hot_enum(RANK.QUEEN) == [0, 0, 0, 0, 0, 0, 1, 0, 0]).all()
    assert (one_hot_enum(RANK.KING) ==  [0, 0, 0, 0, 0, 0, 0, 1, 0]).all()
    assert (one_hot_enum(RANK.ACE) ==   [0, 0, 0, 0, 0, 0, 0, 0, 1]).all()


def test_one_hot_card():
    assert (one_hot_card(None) == np.zeros(FULL_DECK_SIZE)).all()

    expected = np.zeros(FULL_DECK_SIZE)
    expected[9 + 2] = 1
    assert (one_hot_card(Card(RANK.EIGHT, SUIT.HEARTS)) == expected).all()

    k = 0
    for suit in SUIT:
        for rank in RANK:
            expected = np.zeros(FULL_DECK_SIZE)
            expected[k] = 1
            assert (one_hot_card(Card(rank, suit)) == expected).all()
            k += 1


def test_one_hot_card_list():
    M = 100
    for i in range(M):
        cards = np.random.choice(FULL_DECK, 6)
        expected = np.zeros(FULL_DECK_SIZE)
        for c in cards:
            expected[card_ind(c)] = 1
        assert (one_hot_card_list(cards) == expected).all()


def test_one_hot_action_and_card():
    assert (one_hot_action_and_card(ACTION_TYPE.PUT, None) == np.zeros(1 + FULL_DECK_SIZE)).all()
    assert (one_hot_action_and_card(ACTION_TYPE.FINISH, None) == np.concatenate([np.array([1]), np.zeros(FULL_DECK_SIZE)])).all()

    expected = np.zeros(1 + FULL_DECK_SIZE)
    expected[9 + 2 + 1] = 1
    expected[0] = 0
    assert (one_hot_action_and_card(ACTION_TYPE.PUT, Card(RANK.EIGHT, SUIT.HEARTS)) == expected).all()

    for action in ACTION_TYPE:
        k = 0
        for suit in SUIT:
            for rank in RANK:
                expected = np.zeros(1 + FULL_DECK_SIZE)
                expected[1 + k] = 1
                expected[0] = action.value
                assert (one_hot_action_and_card(action, Card(rank, suit)) == expected).all()
                k += 1


def test_create_empty_mask():
    expected = np.zeros(FULL_DECK_SIZE + 1)
    oh = create_empty_mask()
    assert (oh == expected).all()


def test_mark_FINISH_on_mask():
    expected = create_empty_mask()
    expected[0] = 1
    expected[9] = 1
    expected[18] = 1
    mask = create_empty_mask()
    mark_FINISH_on_mask(mask)
    mark_card_on_mask(mask, Card(RANK.ACE, SUIT.SPADES))
    mark_card_on_mask(mask, Card(RANK.ACE, SUIT.HEARTS))
    assert (mask == expected).all()


def test_mark_card_on_mask():
    expected = create_empty_mask()
    expected[0] = 1
    expected[9] = 1
    expected[18] = 1
    mask = create_empty_mask()
    mark_FINISH_on_mask(mask)
    mark_card_on_mask(mask, Card(RANK.ACE, SUIT.SPADES))
    mark_card_on_mask(mask, Card(RANK.ACE, SUIT.HEARTS))
    assert (mask == expected).all()


def test_observation_shape():
    env = Durak_2a_v0()
    env.reset()
    obs = env.get_numpy_observation()
    assert Durak_2a_v0.observation_shape == obs.shape


def test_num_of_actions():
    env = Durak_2a_v0()
    env.reset()
    assert env.num_actions == 37
    assert env.num_actions == FULL_DECK_SIZE + 1
    assert env.num_actions == ACTIONS_WITH_CARDS_NUM


def test_action_card_id_from_str():
    assert [card_ind(card) for card in FULL_DECK] == list(range(FULL_DECK_SIZE))
    
    act_cards = ([(ACTION_TYPE.FINISH, None)]
                 + [(ACTION_TYPE.PUT, card) for card in FULL_DECK])
    exp_ids = list(range(ACTIONS_WITH_CARDS_NUM))
    ids = [action_card_id(*p) for p in act_cards]

    assert exp_ids == ids
    
    ids2 = [action_card_id_from_str(action_card_str(*p)) for p in act_cards]
    
    assert ids2 == ids

    act_cards2 = [action_card_pair_from_str(action_card_str(*p))
                  for p in act_cards]
    
    assert act_cards == act_cards2


@pytest.mark.skip(reason="Test is not implemented")
def test_durak_2a_v0():
    SEED = 145
    env = Durak_2a_v0()
    env.reset(seed=SEED)
    