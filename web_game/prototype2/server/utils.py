""" Вспомогательные функции """  


import shortuuid as su


class FullRoomExc(Exception):
    pass


class RoomNotFoundExc(Exception):
    pass


class SidNotInRoomExc(Exception):
    pass


class UserInfoNotFound(Exception):
    pass


# TODO: Страшный, опасный код. Подумай как переделать.
class Registry:
    def __init__(self):
        self.rooms = dict()
        self.user_infos = dict()
    
    def register_user(self, sid):
        """ Регистрирует пользователя, если он не зарегистрирован """
        if sid not in self.user_infos:
            self.user_infos[sid] = UserInfo()

    def register_room(self, room):
        """ Регистрирует комнату, возвращает имя комнаты """
        self.rooms[room.name] = room
    
    def join_room(self, room_name, sid):
        """ Присоединяет пользователя к комнате
        и комнату к пользователю. """
        if room_name in self.rooms:
            self.rooms[room_name].add_user(sid)
        else:
            raise RoomNotFoundExc()

        self.register_user(sid)
        self.user_infos[sid].add_room(room_name)

    def leave_room(self, room_name, sid):
        """ Отсоединяет пользователя от комнаты
        и комнату от пользователя. """
        if room_name in self.rooms:
            self.rooms[room_name].remove_user(sid)
        else:
            raise RoomNotFoundExc()
        
        self.register_user(sid)
        self.user_infos[sid].remove_room(room_name)
    
    def get_room(self, room_name):
        try:
            return self.rooms[room_name]
        except KeyError:
            raise RoomNotFoundExc()
    
    def get_userInfo(self, sid):
        try:
            return self.user_infos[sid]
        except KeyError:
            raise UserInfoNotFound()
    


class Room:
    def __init__(self, name=None, max_size=2):
        if name is None:
            name = Room.gen_name()
        self.name = name
        self.users = list()
        self.max_size = max_size
        self.host = None
        self.env = None
        self.game_started = False
    
    @staticmethod
    def gen_name():
        """ Генерирует псевдо-уникальное название для комнаты """
        # 2 коллизии на 10**7 (10 миллионов)
        return su.uuid()[:8]

    def user_by_sid(self, sid):
        """ Вернет None, если не найден """
        return next((u for u in self.users if u.sid == sid), None)
    
    def contains(self, sid):
        """ Проверяет есть ли юзер в комнате """
        return next((True for u in self.users if u.sid == sid), False)

    def get_host(self):
        """ Возвращает хоста комнаты """
        return self.host
    
    def set_host(self, sid):
        """ Назначает хостом комнаты """
        host = self.user_by_sid(sid)
        if host is not None:
            self.host = self.user_by_sid(sid)
        else:
            raise SidNotInRoomExc()
    
    def remove_host(self):
        """ Снимает с должности хоста """
        self.host = None

    def add_user(self, sid):
        """ Добавляет юзера в комнату, если он не был добавлен """
        if not self.contains(sid):
            if self.is_full():
                raise FullRoomExc()
            else:
                self.users.append(RoomPlayer(sid))
        
    def remove_user(self, sid):
        """ Удаляет юзера из комнаты """
        if self.host is not None and self.host is self.user_by_sid(sid):
            self.host = None
        self.users = [u for u in self.users if u.sid != sid]
    
    def number_of_users(self):
        """ Возвращает число юзеров """
        return len(self.users)
    
    def is_empty(self):
        """ Пуста ли комната? """
        return self.number_of_users() == 0
    
    def is_full(self):
        """ Полна ли комната """
        return self.number_of_users() == self.max_size
    
    def set_env(self, env):
        """ Среда для игры в дурака """
        self.env = env
    
    def reset_env(self):
        """ Сбросить среду """
        self.env.reset()
    
    def set_ready(self, sid):
        self.user_by_sid(sid).is_ready = True
    
    def is_all_ready(self):
        for user in self.users:
            if not user.is_ready:
                return False
        return True


class RoomPlayer:
    def __init__(self, sid):
        self.sid = sid
        self.is_ready = False


class UserInfo:
    def __init__(self):
        self.rooms = list()
    
    def add_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms.append(room_name)
    
    def remove_room(self, room_name):
        self.rooms = [r for r in self.rooms if r.name != room_name]

