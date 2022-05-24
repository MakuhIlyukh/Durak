from durak.envs import Turn_2a, ACTION_TYPE, TURN_TYPE, Turn_2a_v1


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
        assert turn_2a._turn == post_turns


def check_v1(seq, turn_2a: Turn_2a):
    for action_type, post_player, post_turns in seq:
        turn_2a.turn(action_type)
        assert turn_2a._player == post_player
        assert turn_2a._turn == post_turns


def test_reverse_and_swap():
    turn_2a = Turn_2a()
    turn_2a.reverse_and_swap()
    assert turn_2a._player == 1
    assert turn_2a._turn == [DEFENSE, ATTACK]


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