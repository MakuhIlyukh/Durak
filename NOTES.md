# Правила игры в дурака

## Начало
1. Полная колода перемешивается;
2. Игрокам раздается по 6 карт;
3. Выбирается козырная карта.

## Допустимое количество карт для атаки
```
Допустимое количество = 
    min(кол-во карт у защищающегося на РУКАХ и на СТОЛЕ,
        5 if первый отбой else 6)
```

## Атакующий может положить карту, если:
1. Эта карта есть у игрока на руках;
2. Это начало хода.

ИЛИ

1. Эта карта есть у игрока на руках;
2. Если есть карты на столе с одинаковым value для этой карты;
3. Количество уже лежащих атакующих карт < допустимого количества.

## Защищающийся может побиться, если:
1. Эта карта есть у игрока на руках;
2. Атакующая карта не козырная;
3. Защищающаяся карта козырная.

ИЛИ

1. Эта карта есть у игрока на руках;
2. Масти атакующей и защищающейся карты совпадают;
3. Value атакующей < Value Защищающейся.

## Пополнение карт
1. Сначала берет карты из колоды игрок, который атаковал;
2. Потом берет из колоды карты игрок, который защищался.

## Завершение игры
Не осталось карт у одного из игроков.
Проверяется во время начала атаки.

# Идеи и предложения

# TODO LIST
- [ ] MLFLOW integration
- [ ] rllib
- [ ] PettingZoo
- [ ] Добавить README в подпапки
- [ ] Добавить логирование