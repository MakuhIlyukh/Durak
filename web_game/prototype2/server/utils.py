""" Вспомогательные функции """  


import shortuuid as su

# TODO: Страшный, опасный код. Подумай как переделать.
class RoomRegistry:
    def __init__(self):
        self.rooms = dict()
        self.user_rooms = dict()
    
    def create_room(self):
        room = Room()
        self.rooms[room.name] = room
        return room.name
    
    def join_room(self, room_name, sid):
        if room_name in self.rooms:
            self.rooms[room_name].add_user(sid)
        else:
            raise RoomNotFoundExc()

        if sid not in self.user_rooms:
            self.user_rooms[sid] = set()
        self.user_rooms[sid].add(room_name)

    def leave_room(self, room_name, sid):
        if room_name in self.rooms:
            self.rooms[room_name].remove_user(sid)
        else:
            raise RoomNotFoundExc()
        
        if sid not in self.user_rooms:
            self.user_rooms[sid] = set()
        self.user_rooms[sid].remove(room_name)
    
    def set_host(self, room_name, sid):
        self.rooms[room_name].set_host(sid)


class FullRoomExc(Exception):
    pass


class RoomNotFoundExc(Exception):
    pass

class SidNotInRoomExc(Exception):
    pass


class Room:
    def __init__(self, name=None, max_size=2):
        if name is None:
            name = Room.gen_name()
        self.name = name
        self.users = set()
        self.is_ready = dict()
        self.max_size = max_size
        self.host = None
        self.env = None
    
    @staticmethod
    def gen_name():
        """ Генерирует псевдо-уникальное название для комнаты """
        # 2 коллизии на 10**7 (10 миллионов)
        return su.uuid()[:8]
    
    def get_host(self):
        """ Возвращает хоста комнаты """
        return self.host
    
    def set_host(self, sid):
        """ Назначает хостом комнаты """
        if sid in self.users:
            self.host = sid
        else:
            raise SidNotInRoomExc()
    
    def remove_host(self):
        """ Снимает с должности хоста """
        self.host = None

    def add_user(self, user):
        """ Добавляет юзера в комнату """
        if self.is_full():
            raise FullRoomExc()
        else:
            self.users.add(user)
            self.is_ready[user] = False
    
    def remove_user(self, user):
        """ Удаляет юзера из комнаты """
        # ???: Надо обрабатывать случай, когда юзверь
        #      не находится уже в комнате?
        self.users.remove(user)
        del self.is_ready[user]
    
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
        self.env = env
    
    def reset_env(self):
        self.env.reset()
    
    def create_mapping(self):
        self.mapping = dict()
        for i, u in enumerate(self.users):
            self.mapping[i] = u 


class RoomPlayer:
    def __init__(self, sid):
        self.sid = sid
        self.is_ready = False



