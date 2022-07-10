""" Мультиагентные среды для игры в дурака """
# TODO: избавься от типизации везде или добавь ее
# TODO: pep8 codestyle check
# TODO: измени Card на Optional[Card] = None
# TODO: от PUT можно избавиться, если передавать None вместо карты
# TODO: посмотри, как можно оптимизировать fsm из transitions
#       с помощью её конфигурирования


# %% imports
from typing import Optional, List

import numpy as np
from gym.core import Env
from transitions import Machine

from durak.envs.transitions_extension import MayMachine
from durak.envs.durak_2a_v0.action import ACTION_TYPE
from durak.envs.durak_2a_v0.states import TURN_TYPE
from durak.envs.durak_2a_v0.card import (
    Card, FULL_DECK, less)
from durak.envs.durak_2a_v0.utils import (
    card_ind, create_empty_mask, mark_FINISH_on_mask,
    mark_card_on_mask, one_hot_enum, one_hot_card, one_hot_card_list)


MIN_PLAYER_CARDS = 6
""" Минимальное число карт у игрока на руке """
MAX_PAIRS_NUMBER_BEFORE_FIRST_BEAT = 5
""" Первый отбой 5 (пар) карт """
FIRST_PLAYER_INDEX = 0
""" Номер первого игрока """
SECOND_PLAYER_INDEX = 1
""" Номер второго игрока """

# НАГРАДЫ
LOSS_REWARD = -1
WIN_REWARD = 1
DRAW_REWARD = 0
INVALID_REWARD = -5


# ???: Удовлетворяет ли среда критериям наследия от Env?
# ANSWER: step не возвращает награды и наблюдения, поэтому не особо.
# ???: А влияет ли это на работоспособность среды и системы?
# TODO: Проверить работоспособность MayMachine
class Durak_2a_v0(Env):
    _transitions = [
        # end of game (PUT ACTION)
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.DRAW,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_draw_cond"]
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.WIN,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_win_cond"]
        },
        {
            "trigger": ACTION_TYPE.PUT.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.LOSS,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_loss_cond"]
        },
        # end of game (FINISH ACTION)
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.DRAW,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_draw_cond"]
        },
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.WIN,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_win_cond"]
        },
        {
            "trigger": ACTION_TYPE.FINISH.name,
            "source": TURN_TYPE.START_ATTACK,
            "dest": TURN_TYPE.LOSS,
            "before": [],  # ???: Need to add anything?
            "conditions": ["_put_or_finish_start_attack_to_loss_cond"]
        },
        # game
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

    def __init__(self, seed: Optional[int] = None):
        self._machine = MayMachine(
            model=self,
            states=TURN_TYPE,
            initial=TURN_TYPE.START_ATTACK,
            transitions=self._transitions
        )
        self.reset(seed)

    def reset(self, seed: Optional[int] = None):
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
        self.done = False
        """ Флаг окончания игры """

    def _get_observation(self):
        """ Получить наблюдения для ходящего игрока """
        # TODO: Стоит определиться с dtype
        obs = []
        # setting state
        obs.append(one_hot_enum(self.state))
        # setting trump card
        obs.append(one_hot_card(self._trump_card))
        # setting player's hand
        obs.append(one_hot_card_list(self._cards[self._player]))
        # setting other player's hand SIZE
        obs.append(np.array([len(self._cards[self._other_player])]))
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
        # setting first beat
        obs.append(np.array([int(self._first_beat)]))  # TODO: dtype?

        return np.concatenate(obs)

    def _step(self,
              action_type: ACTION_TYPE,
              card: Optional[Card]):
        """ Выполняет действие """
        # do action (or not if it's invalid)
        if not self.trigger(action_type.name, card):
            self.to_INVALID()
        raise NotImplementedError("Допиши :)")

    def _one_hot_valid_actions(self):
        """ Возвращает маску валидных действий """
        res = create_empty_mask()
        # Если выполнить действие FINISH
        if self.may_FINISH(None):
            mark_FINISH_on_mask(res)
        # Если можно выполнить действие PUT
        # NOTE: проверяется ТОЛЬКО для карт на РУКЕ
        #       поэтому может быть источником багов,
        #       если возможны действия с картами НЕ на руке
        for card in self._cards[self._player]:
            if self.may_PUT(card):
                mark_card_on_mask(res, card)
        return res

    # ===========================================
    # enter callbacks
    # ===========================================
    def on_enter_START_ATTACK(self, card: Optional[Card]):
        # FINISH выполнится, если игра должна завершиться,
        # поэтому мы перескочим в другое состояние(WIN, LOSS, DRAW).
        # Не бойтесь, в INVALID перейти нельзя, если нет такого transition
        self.FINISH(None)

    def on_enter_WIN(self, card: Optional[Card]):
        self._set_rewards(WIN_REWARD, LOSS_REWARD)
        self.done = True

    def on_enter_LOSS(self, card: Optional[Card]):
        self._set_rewards(LOSS_REWARD, WIN_REWARD)
        self.done = True

    def on_enter_DRAW(self, card: Optional[Card]):
        self._set_rewards(DRAW_REWARD, DRAW_REWARD)
        self.done = True

    def on_enter_INVALID(self, card: Optional[Card]):
        self._set_rewards(INVALID_REWARD, DRAW_REWARD)
        self.done = True

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

    def _put_or_finish_start_attack_to_draw_cond(self, card: Optional[Card]):
        """ Ничья если: """
        return (
            not bool(self._cards[self._player])
            and
            not bool(self._cards[self._other_player])
        )

    def _put_or_finish_start_attack_to_win_cond(self, card: Optional[Card]):
        """ Победа текущего игрока, если: """
        return (
            not bool(self._cards[self._player])
            and
            bool(self._cards[self._other_player])  # TODO: maybe redudant
        )

    def _put_or_finish_start_attack_to_loss_cond(self, card: Optional[Card]):
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

    def _finish_attack_callback(self, card: Optional[Card]):
        # Пополняем бито
        self._beat.extend(self._table[self._player])
        self._beat.extend(self._table[self._other_player])
        self._first_beat = False
        # Очищаем стол
        self._clear_table()
        # Берем карты из колоды
        self._pop_cards_from_deck()

    def _finish_succ_attack_callback(self, card: Optional[Card]):
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
        Не работает для состояний win, loss, draw, invalid. """
        if self.state in (TURN_TYPE.ATTACK,
                          TURN_TYPE.START_ATTACK,
                          TURN_TYPE.SUCC_ATTACK):
            return self._player
        else:
            return self._other_player

    def _defending_player(self):
        """ Возвращает защищающегося игрока.
        Не работает для состояний win, loss, draw, invalid. """
        if self.state in (TURN_TYPE.DEFENSE,):
            return self._player
        else:
            return self._other_player

    def _clear_table(self):
        self._table = [[], []]

    def _new_deck(self) -> List[Card]:
        """ Создает случайную колоду """
        res = list(FULL_DECK)
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
