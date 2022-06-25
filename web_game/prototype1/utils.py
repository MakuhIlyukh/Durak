""" Вспомогательные функции """  


import shortuuid as su


class Room:
    def __init__(self, name=None, max_size=2):
        if name is None:
            name = Room.gen_name()
        self.name = name
        self.users = []
        self.max_size = max_size
        self.host = None
        """ Кто хост комнаты? """
    
    @staticmethod
    def gen_name():
        """ Генерирует всевдо-уникальное название для комнаты """
        # 2 коллизии на 10**7 (10 миллионов)
        return su.uuid()[:8]
    
    def get_host(self):
        """ Возвращает хоста комнаты """
        raise NotImplementedError()

    def add_user(self, user):
        """ Добавляет юзера в комнату """
        if self.is_full():
            # ???: Как вернуть сообщение, о том что в комнату
            #      нельзя добавить больше людей
            pass
        raise NotImplementedError()
    
    def remove_user(self, user):
        """ Удаляет юзера из комнаты """
        # ???: Надо обрабатывать случай, когда юзверь
        #      не находится уже в комнате?
        raise NotImplementedError()
    
    def number_of_users(self):
        """ Возвращает число юзеров """
        return len(self.users)
    
    def is_empty(self):
        """ Пуста ли комната? """
        return self.number_of_users() == 0
    
    def is_full(self):
        """ Полна ли комната """
        return self.number_of_users() == self.max_size
