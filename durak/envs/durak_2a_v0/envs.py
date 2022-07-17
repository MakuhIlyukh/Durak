""" Мультиагентные среды для игры в дурака """
# TODO: избавься от типизации везде или добавь ее
# TODO: pep8 codestyle check
# TODO: измени Card на Optional[Card] = None
# TODO: от PUT можно избавиться, если передавать None вместо карты
# TODO: посмотри, как можно оптимизировать fsm из transitions
#       с помощью её конфигурирования


# %% imports
from typing import Optional, List
from copy import deepcopy

import numpy as np
from gym.core import Env as GymEnv
from gym.error import ResetNeeded
from rlcard.envs import Env as RLCardEnv

from durak.envs.transitions_extension import MayMachine
from durak.envs.durak_2a_v0.action import ACTION_TYPE
from durak.envs.durak_2a_v0.states import TURN_TYPE
from durak.envs.durak_2a_v0.card import (
    FULL_DECK_SIZE, Card, FULL_DECK, less)
from durak.envs.durak_2a_v0.utils import (
    ACTIONS_WITH_CARDS_NUM, action_card_id, action_card_pair_from_str, action_card_str,
    action_card_str_from_id, card_ind, create_empty_mask,
    mark_FINISH_on_mask, mark_card_on_mask, one_hot_enum, one_hot_card,
    one_hot_card_list)


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
class Durak_2a_v0(GymEnv):
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

    num_players = 2
    """ Число игроков """
    num_actions = ACTIONS_WITH_CARDS_NUM
    """ Число действий """
    observation_shape = (226,)
    """ Размерность пространства наблюдений """
    # TODO: В будующем добавь поле observation_space:
    # TODO: Какой тип observation space
    # observation_space = Obser

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

    def get_numpy_observation(self):
        """ Получить наблюдения для ходящего игрока (numpy.ndarray) """
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
        # setting beat
        obs.append(one_hot_card_list(self._beat))

        return np.concatenate(obs)
    
    def get_observation(self):
        """ Получить наблюдения для ходящего игрока в dict-формате. """
        return {
            "state": self.state,
            "trump_card": self._trump_card,
            "cards": deepcopy(self._cards[self._player]),
            "enemy_len": len(self._cards[self._other_player]),
            "table": deepcopy(self._table[self._player]),
            "enemy_table": deepcopy(self._table[self._other_player]),
            "last_card": (self._table[self._other_player][-1]
                          if bool(self._table[self._other_player])
                          else None),
            "first_beat": self._first_beat,
            "beat": deepcopy(self._beat)
        }
    
    def get_terminal_observation(self, player):
        if player == self._player:
            state = self.state
        else:
            if self.state is TURN_TYPE.WIN:
                state = TURN_TYPE.LOSS
            elif self.state is TURN_TYPE.LOSS:
                state = TURN_TYPE.WIN
            elif self.state is TURN_TYPE.DRAW:
                state = TURN_TYPE.DRAW
            elif self.state is TURN_TYPE.INVALID:
                state = TURN_TYPE.DRAW
        return {'state': state}
    
    def do_step(self,
                action_type: ACTION_TYPE,
                card: Optional[None]):
        """ Делает шаг """
        if self.done:
            raise ResetNeeded("Нужно вызвать reset!")
        if not self.trigger(action_type.name, card):
            self.to_INVALID()

    def legal_actions(self):
        """ Возвращает СПИСОК валидных действий и карт """
        res = []
        # Если выполнить действие FINISH
        if self.may_FINISH(None):
            res.append((ACTION_TYPE.FINISH, None))
        # Если можно выполнить действие PUT
        # NOTE: проверяется ТОЛЬКО для карт на РУКЕ
        #       поэтому может быть источником багов,
        #       если возможны действия с картами НЕ на руке
        for card in self._cards[self._player]:
            if self.may_PUT(card):
                res.append((ACTION_TYPE.PUT, card))
        return res

    def legal_actions_mask(self):
        """ Возвращает МАСКУ валидных действий и карт """
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

    def get_perfect_state(self):
        """ Возвращает полное состояние среды в дикт-формате.
        
        Удобно, чтобы pickl'ить.
        """
        return {
            "player": self._player,
            "other_player": self._other_player,
            "state": self.state,
            "first_beat": self._first_beat,  
            "deck": deepcopy(self._deck),
            "cards": deepcopy(self._cards),
            "beat": deepcopy(self._beat),
            "table": deepcopy(self._table),
            "trump_card": self._trump_card,
            "rewards": deepcopy(self.rewards),
            "done": self.done
        }

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
            bool(self._cards[self._other_player])
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
            bool(self._cards[self._other_player])
        )

    def _put_or_finish_start_attack_to_loss_cond(self, card: Optional[Card]):
        """ Проигрыш текущего игрока, если: """
        return (
            bool(self._cards[self._player])
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
        """ Очищает стол """
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


class Durak_2a_v0_game:
    """ Класс обертка над Durak_2a_v0.
    
    Нужен, чтобы интегрировать в rlcard.
    """
    def __init__(self):
        # Не самое элегантное решение использовать
        #  одновременно GymEnv and RLCardEnv.
        self.denv = Durak_2a_v0()
        # Пока не реализована возможность вернуться на предыдущий шаг
        self.allow_step_back = False
        self.num_players = self.denv.num_players
        self.num_actions = self.denv.num_actions
    
    def configure(self, game_config: dict):
        """ Эта штука для чего-то существует """
        pass
    
    def init_game(self):
        """ Resets the game """
        self.denv.reset()
        player = self.denv._player
        state = self.get_state(player)
        return state, player

    def step(self, action: str):
        """ Шаг.
        
        Возвращает наблюдения для игрока(который будет ходить далее)
        и индекс ходящего игрока. 
        """
        self.denv.do_step(*action_card_pair_from_str(action))
        return self.get_state(self.denv._player), self.denv._player

    def step_back(self):
        """ Возвращение на предыдущее состояние игры. """
        # Можно заменить на return False
        raise NotImplementedError("Пока не нуждается в реализации")

    def get_state(self, player_id: int):
        """ Возвращает состояние для данного игрока """
        if player_id != self.denv._player:
            if self.denv.done:
                return self.denv.get_terminal_observation(player_id)
            raise ValueError("Невозможно получить состояние для неходящего игрока!")
        state = self.denv.get_observation()
        state['numpy_obs'] = self.denv.get_numpy_observation()
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.denv._player
        state['legal_actions'] = self.denv.legal_actions()
        return state
    
    def get_perfect_state(self):
        """ Возвращает полное состояние среды """
        state = self.denv.get_perfect_state()
        state['num_players'] = self.denv.num_players
        state['legal_actions'] = self.denv.get_legal_actions()


    def get_payoffs(self):
        """ Возвращает награды """
        return deepcopy(self.denv.rewards)
    
    def get_legal_actions(self):
        """ Возвращает разрешенные действия в строковом
        представлении.
        """
        return [action_card_str(*pair)
                for pair in self.denv.legal_actions()]

    def get_num_players(self):
        """ Возвращает число игроков """
        return self.num_players
    
    def get_num_actions(self):
        """ Возвращает число всех возможных действий """
        return self.num_actions

    def get_player_id(self):
        """ Возвращает номер ходящего игрока """
        return self.denv._player

    def is_over(self):
        """ Завершен ли эпизод? """
        return self.denv.done
    
    def get_state_shape(self):
        """ Возвращает размерность пространства наблюдений для одного
        игрока.
        """
        return self.denv.observation_shape
    
    def denv_seed(self, seed):
        """ Устанавливает seed для Durak_2a_v0 """
        self.denv.seed(seed)
    
    def get_legal_actions_ids(self):
        """  Возвращает список из id допустимых действий. """
        return [action_card_id(*pair)
                for pair in self.denv.legal_actions()]


class Durak_2a_v0_rlcard(RLCardEnv):
    """ Класс обертка над Durak_2a_v0_game
    
    Нужен, чтобы использовать алгоритмы из rlcard.
    """
    def __init__(self, config):
        self.name = "Durak_2a_v0"
        self.game = Durak_2a_v0_game()
        super().__init__(config)
        self.state_shape = [self.game.get_state_shape()
                            for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        """ Возвращает награды """
        # ???: почему np.array, а не list
        return np.array(self.game.get_payoffs())

    def get_perfect_information(self):
        raise NotImplementedError("Не хочу реализовывать. Вроде и не требуется.")

    def seed(self, seed: Optional[int] = None):
        """ Resets random number generators """
        super().seed(seed)
        self.game.denv_seed(seed)

    def _extract_state(self, state):
        obs = state['numpy_obs']
        legal_action_id = self._get_legal_actions()
        extracted_state = {'obs': obs, 'legal_actions': legal_action_id}
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = deepcopy(state['legal_actions'])
        extracted_state['action_recorder'] = self.action_recorder
        return extracted_state

    def _decode_action(self, action_id):
        """ Возвращает строковое предствление действия из id """
        return action_card_str_from_id(action_id)

    def _get_legal_actions(self):
        """ Возвращает список из id допустимых действий. """
        return {act_id: None
                for act_id in self.game.get_legal_actions_ids()}


# %%
