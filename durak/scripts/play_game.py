"""
Для ручного тестирования Durak_2a_v0.
"""


import pickle
import traceback

from transitions import MachineError
from termcolor import colored

from durak.envs.durak_2a_v0.action import ACTION_TYPE
from durak.envs.durak_2a_v0.envs import Durak_2a_v0


class InvalidCommandExc(Exception):
    pass


def print_info(env):
    print(f"\n\n\nХОД")

    def cld(s, player):
        return colored(s, "green" if player == 0 else "yellow")

    print(cld(f"Ходит игрок: ", env._player), end="")
    print(cld(env._player, env._player))
    
    print(f"Тип хода: {env.state}")
    print(cld(f"Карты игрока 0: {env._cards[0]}  ({len(env._cards[0])})", 0))
    print(cld(f"Карты игрока 1: {env._cards[1]}  ({len(env._cards[1])})", 1))
    print(cld(f"Стол игрока 0: {env._table[0]}", 0))
    print(cld(f"Стол игрока 1: {env._table[1]}", 1))
    print(f"Колода: {env._deck}")
    print(f"БИТО: {env._beat}")


def parse_command(env, com):
    all_commands = [
        "p", "f", "q"
    ]
    if com == 'f':
        return ACTION_TYPE.FINISH, None
    else:
        tokens = com.split(' ')
        if len(tokens) == 2 and tokens[0] == 'p':
            try:
                card_ind = int(tokens[1])
            except ValueError:
                raise InvalidCommandExc("int fail")
            if card_ind < len(env._cards[env._player]):
                return ACTION_TYPE.PUT, env._cards[env._player][card_ind]
            else:
                raise InvalidCommandExc("invalid index of card")
        else:
            raise InvalidCommandExc("Не удовлетворяет формату p {digit} ИЛИ f")


def play():
    history = list()
    try:
        env = Durak_2a_v0()
        env.reset(seed=145)

        print_info(env)
        com = input()
        history.append((None, pickle.dumps(env)))
        while com != 'q':
            try:
                action, card = parse_command(env, com)
                env.trigger(action.name, card)
                history.append((action, pickle.dumps(env)))
            except InvalidCommandExc as e:
                print(f"\n\n\nНеправильная команда.{e}")
            # except MachineError:
                # print(f"\n\n\nДействие невозможно")
            print_info(env)
            com = input()
    except Exception as e:
        traceback.print_exc()
        print("\n\nВсе сохранено в history")
    finally:
        return history


if __name__ == '__main__':
    history = play()