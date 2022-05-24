from random import choice

import numpy as np
from transitions import MachineError
from tqdm import tqdm

from durak.envs import (
    Turn_2a, ACTION_TYPE, TURN_TYPE, Turn_2a_v1, Turn_2a_v2,
    UnknownTransitionError
)

# Short aliases
# Actions
PUT = ACTION_TYPE.PUT
TAKE = ACTION_TYPE.TAKE
FINISH = ACTION_TYPE.FINISH
# Turns
ATTACK = TURN_TYPE.ATTACK
ATTACK_END = TURN_TYPE.ATTACK_END
DEFENSE = TURN_TYPE.DEFENSE
DEFENSE_END = TURN_TYPE.DEFENSE_END
START = TURN_TYPE.START


# functions
def check(seq, turn_2a: Turn_2a):
    for action_type, post_player, post_turns in seq:
        turn_2a.turn(action_type)
        assert turn_2a._player == post_player
        assert turn_2a._other_player != turn_2a._player
        assert turn_2a.state == post_turns


def check_v1(seq, turn_2a: Turn_2a_v1):
    for action_type, post_player, post_turns in seq:
        turn_2a.turn(action_type)
        assert turn_2a._player == post_player
        assert turn_2a.state == post_turns


def test_reverse_and_swap():
    turn_2a = Turn_2a()
    turn_2a.reverse_and_swap()
    assert turn_2a._player == 1
    assert turn_2a.state == [DEFENSE, ATTACK]


def check_v2(seq, turn_2a: Turn_2a_v2):
    for action_type, post_player, post_turns in seq:
        turn_2a.turn(action_type)
        assert turn_2a._player == post_player
        assert turn_2a.state == post_turns


def test_Turn_2a():
    # action_type, post_player, post_turns
    seq = [
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет первую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет вторую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет третью карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (FINISH, 1, [DEFENSE, ATTACK]),  # 0: БИТО!

        (PUT, 0, [DEFENSE, ATTACK]),  # 1: атакует первой картой
        (PUT, 1, [DEFENSE, ATTACK]),  # 0: побивается
        (FINISH, 0, [ATTACK, DEFENSE]),  # 1: БИТО!
    ]
    turn_2a = Turn_2a()
    check(seq, turn_2a)

    seq = [
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет первую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет вторую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет третью карту
        (TAKE, 0, [ATTACK_END, DEFENSE_END]),  # 1: берет
        (PUT, 1, [ATTACK_END, DEFENSE_END]),  # 0: дает догонку
        (TAKE, 0, [ATTACK_END, DEFENSE_END]),  # 1: берет
        (FINISH, 0, [ATTACK, DEFENSE]),  # 0: Закончил давать вдогонку

        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет первую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет вторую карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (PUT, 1, [ATTACK, DEFENSE]),  # 0: кладет третью карту
        (PUT, 0, [ATTACK, DEFENSE]),  # 1: побивается
        (FINISH, 1, [DEFENSE, ATTACK]),  # 0: БИТО!
    ]
    turn_2a.reset()
    check(seq, turn_2a)


def test_Turn_2a_v1():
    seq = [
        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (PUT, 0, ATTACK),  # 1: побивается
        (FINISH, 1, START),  # 0: БИТО!

        (PUT, 0, DEFENSE),  # 1: атакует первой картой
        (PUT, 1, ATTACK),  # 0: побивается
        (FINISH, 0, START),  # 1: БИТО!
    ]
    turn_2a_v1 = Turn_2a_v1()
    check_v1(seq, turn_2a_v1)

    seq = [
        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (TAKE, 0, ATTACK_END),  # 1: берет
        (PUT, 0, ATTACK_END),  # 0: дает в догонку
        (PUT, 0, ATTACK_END),  # 0: дает в догонку
        (FINISH, 0, START),  # 0: Закончил давать вдогонку

        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (PUT, 0, ATTACK),  # 1: побивается
        (FINISH, 1, START),  # 0: БИТО!
    ]
    turn_2a_v1.reset()
    check_v1(seq, turn_2a_v1)


def test_turn_2a_v2():
    seq = [
        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (PUT, 0, ATTACK),  # 1: побивается
        (FINISH, 1, START),  # 0: БИТО!

        (PUT, 0, DEFENSE),  # 1: атакует первой картой
        (PUT, 1, ATTACK),  # 0: побивается
        (FINISH, 0, START),  # 1: БИТО!
    ]
    turn_2a_v2 = Turn_2a_v2()
    check_v2(seq, turn_2a_v2)

    seq = [
        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (TAKE, 0, ATTACK_END),  # 1: берет
        (PUT, 0, ATTACK_END),  # 0: дает в догонку
        (PUT, 0, ATTACK_END),  # 0: дает в догонку
        (FINISH, 0, START),  # 0: Закончил давать вдогонку

        (PUT, 1, DEFENSE),  # 0: кладет первую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет вторую карту
        (PUT, 0, ATTACK),  # 1: побивается
        (PUT, 1, DEFENSE),  # 0: кладет третью карту
        (PUT, 0, ATTACK),  # 1: побивается
        (FINISH, 1, START),  # 0: БИТО!
    ]
    turn_2a_v2.reset()
    check_v2(seq, turn_2a_v2)


def test_turn_2a_v1_and_v2():
    # number of episodes
    M = 10**4
    # length of episode
    N = 100
    SEED = 4525
    
    np.random.seed(SEED)
    all_actions = list(ACTION_TYPE)
    v1 = Turn_2a_v1()
    v2 = Turn_2a_v2()
    for i in tqdm(range(M)):
        v1.reset()
        v2.reset()
        for j in range(N):
            action = all_actions[np.random.choice(len(all_actions))]
            
            v1_exc = False
            try:
                v1.turn(action)
            except UnknownTransitionError:
                v1_exc = True

            v2_exc = False
            try:
                v2.turn(action)
            except (AttributeError, MachineError):
                v2_exc = True

            assert v1_exc == v2_exc
            if not (v1_exc or v2_exc):
                assert v1._player == v2._player
                assert v1.state == v2.state
            
            