import random
import sys


class BoardExceptions(Exception):
    def __str__(self):
        return "Какой-то странный exception."


class BoardOutException(BoardExceptions):
    def __str__(self):
        return "Выстрел мимо доски"


class UserInputException(BoardExceptions):
    def __str__(self):
        return "Неправильный ввод. Пожалуйста повторите."


class BoardAlreadyException(BoardExceptions):
    def __str__(self):
        return "Уже стреляли сюда, повторите ввод."


class BoardShipPlaceException(BoardExceptions):
    def __str__(self):
        return "Что-то не так с размещением корабля."


class Dot():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"P({self.x}, {self.y})"


class Ship():
    def __init__(self, cone, length, direct):
        self.length = length
        self.point = cone
        self.dir = direct
        self.lives = length

#Возвращает список точек корабля
    @property
    def shipdots(self):
        dots = []
        x_ = self.point.x
        y_ = self.point.y
        for _ in range(self.length):
            dots.append(Dot(x_, y_))
            if self.dir == 0:
                x_ += 1
            else:
                y_ += 1
        return dots

#Возвращает True, если произвольная точка в списке точек корабля
    def isshooten(self, point):
        return (point in self.shipdots)


class Board():
    def __init__(self, size, hide=False):
        self.boardsize = size
        self.hide = hide
        self.hitships = 0
        self.live_ships = 0
        self.board = [["_"]*self.boardsize for _ in range(self.boardsize)]

        self.busydots = []
        self.ships = []

#Добавляет корабль на доску
    def add_ship(self, ship):
        for d in ship.shipdots:
            if self.isoutboard(d) or d in self.busydots:
                raise BoardShipPlaceException
        for d in ship.shipdots:
            self.board[d.x][d.y] = "█"
            self.busydots.append(d)

        self.live_ships += 1
        self.ships.append(ship)
        self.contour(ship)

#Определяет точки вокруг корабля, его контур
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.shipdots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)

                if not (self.isoutboard(cur)) and cur not in self.busydots:
                    if verb:
                        self.board[cur.x][cur.y] = "∙"
                    self.busydots.append(cur)

#Определяет, что точка вне игрового поля
    def isoutboard(self, point):
        return not (0 <= point.x < self.boardsize and 0 <= point.y < self.boardsize)

#Делает "выстрел" в точку текущей доски
    def shot(self, point):
        if self.isoutboard(point):
            raise BoardOutException()

        if point in self.busydots:
            raise BoardAlreadyException()

        self.busydots.append(point)

        for ship in self.ships:
            if ship.isshooten(point):
                ship.lives -= 1
                self.board[point.x][point.y] = "X"

                if ship.lives == 0:
                    self.hitships += 1
                    self.live_ships -= 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль подбит!")
                    return True

        self.board[point.x][point.y] = "∙"
        print("Мимо!")
        return False

    def begin(self):
        self.busydots = []


class Player():

    def __init__(self, enemy_board):
        self.pref_moves = []
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                return self.enemy_board.shot(self.ask())
            except BoardAlreadyException as e:
                print(e)


class Ai_Player(Player):

#Определяет ход компьютера. Выбор либо из всех свободных полей, либо из полей вокруг недобитого корабля
    def ask(self):
        self.get_pref_moves()
        if len(self.pref_moves) > 0:
            d = random.choice(self.pref_moves)
        else:
            self.get_free_moves()
            d = random.choice(self.pref_moves)

        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

#Определяет предпочтительные точки для выстрела компьютера, если есть недобитый корабль
    def get_pref_moves(self):
        self.pref_moves = []
        pref_h = [(0, -1), (0, 1)]
        pref_v = [(-1, 0), (1, 0)]
        pref = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for x in range(self.enemy_board.boardsize):
            for y in range(self.enemy_board.boardsize):
                orient = -1
                if self.enemy_board.board[x][y] == "X":
                    for dx, dy in pref_v:
                        cur = Dot(x + dx, y + dy)
                        if not (self.enemy_board.isoutboard(cur)) and self.enemy_board.board[x + dx][y + dy] == "X":
                            orient = 1
                        if orient == 1:
                            cur = Dot(x - dx, y)
                            if not (self.enemy_board.isoutboard(cur)) and cur not in self.enemy_board.busydots:
                                self.pref_moves.append(cur)

                    for dx, dy in pref_h:
                        cur = Dot(x + dx, y + dy)
                        if not (self.enemy_board.isoutboard(cur)) and self.enemy_board.board[x + dx][y + dy] == "X":
                            orient = 0
                        if orient == 0:
                            cur = Dot(x, y - dy)
                            if not (self.enemy_board.isoutboard(cur)) and cur not in self.enemy_board.busydots:
                                self.pref_moves.append(cur)

                    if orient == -1:
                        for dx, dy in pref:
                            cur = Dot(x + dx, y + dy)
                            if not (self.enemy_board.isoutboard(cur)) and cur not in self.enemy_board.busydots:
                                self.pref_moves.append(cur)

        return

#Определяет все доступные, неподстреленные ранее точки доски
    def get_free_moves(self):
        self.pref_moves = []
        for x in range(self.enemy_board.boardsize):
            for y in range(self.enemy_board.boardsize):
                if not (self.enemy_board.isoutboard(Dot(x, y))) and Dot(x, y) not in self.enemy_board.busydots:
                    self.pref_moves.append(Dot(x, y))

        return


class User(Player):

    def ask(self):
        while True:
            cords = input("Введите строку и столбец для выстрела, через пробел. Ваш ход: ").split()

            if len(cords) == 1 and cords[0].isdigit() and int(cords[0]) == 0:
                print("До свидания!")
                sys.exit()

            if len(cords) < 2 or not cords[0].isdigit() or not cords[1].isdigit() or int(cords[0]) > self.enemy_board.boardsize or int(cords[1]) > self.enemy_board.boardsize:
                print("Вы ввели некорректные данные. Не ошибайтесь при вводе.")
                continue

            return Dot(int(cords[0]) - 1, int(cords[1]) - 1)


class Game():

    def __init__(self, size, ships):
        if size < 4 or size > 9:
            print("Допустимо поле от 4х4, не более 9х9.")
            sys.exit()
        sum_ = 0
        for i in ships:
            sum_ += int(i) + 2

        if sum_ > size * size:
            print(f"Всего клеток {size ** 2}, для кораблей нужно {sum_}.")
            print("Не смогу разместить столько кораблей.")
            sys.exit()

        self.size = size
        self.squadron = ships
        self.userboard = self.randomboard()
        self.aiboard = self.randomboard()
        self.aiboard.hide = True
        self.User = User(self.aiboard)
        self.Ai = Ai_Player(self.userboard)
        pass

#Вывод полей игрока и компьютера
    def __str__(self):
        print("    Поле игрока" + " " * 4 * self.size + "Поле компьютера")
        print("-" * (4 * self.size + 3) * 2 + "-" * 8)
        res = "  |"
        for i in range(1, self.userboard.boardsize + 1):
            res = res + " " + str(i) + " |"
        res = res + " " * 10 + "|"
        for i in range(1, self.aiboard.boardsize + 1):
            res = res + " " + str(i) + " |"

        for i in range(self.size):

            res += f"\n{i + 1}" + " | " + " | ".join(self.userboard.board[i]) + " |"
            res += " " * 8
            if self.userboard.hide:
                res = res.replace("█", "_")
            res1 = f"{i + 1}" + " | " + " | ".join(self.aiboard.board[i]) + " |"
            if self.aiboard.hide:
                res1 = res1.replace("█", "_")
            res = res + res1

        return res

    def randomboard(self):
        board = None
        while board is None:
            board = self.fillboard()
        return board

#Заполнение доски компьютера и игрока кораблями
    def fillboard(self):
        lens = self.squadron
        board = Board(self.size)

        for l in lens:

            attempts = 0
            while True:
                if attempts > 20:
                    return None

                d = Dot(random.randint(0, self.size), random.randint(0, self.size))
                v = random.randint(0, 1)

                ship = Ship(d, l, v)
                try:
                    board.add_ship(ship)
                    break
                except BoardShipPlaceException:
                    attempts += 1
                    pass

        board.begin()
        return board

    def greet(self):
        print("Морской бой. Человек vs Компьютер")
        print("Правила:")
        print("1. Человек ходит первым.")
        print("2. Указывается строка и столбец для выстрела по вражескому полю.")
        print("3. Если нет попадания, переход хода к другому игроку.")
        print("4. Если попали, делаете еще ход.")
        print("5. Игра заканчивается, когда все корабли игрока потоплены.")
        print("-" * (4 * self.size + 3) * 2 + "-" * 8)
        print("Внимание! Компьютер не прощает ошибок, он добивает уже подбитый корабль!")
        print("-" * (4 * self.size + 3) * 2 + "-" * 8)

#Основной игровой цикл
    def loop(self):
        num = 0
        while True:
            print(self)

            if num % 2 == 0:
                print("-" * (4 * self.size + 3) * 2 + "-" * 8)
                print("Ход игрока!")
                repeat = self.User.move()
            else:
                print("-" * (4 * self.size + 3) * 2 + "-" * 8)
                print("Ход компьютера!")
                repeat = self.Ai.move()

            print("-" * (4 * self.size + 3) * 2 + "-" * 8)
            print(f"У игрока осталось {self.userboard.live_ships} кораблей, уже подбито {self.userboard.hitships}")
            print(f"У компьютера осталось {self.aiboard.live_ships} кораблей, уже подбито {self.aiboard.hitships}.")
            print("-" * (4 * self.size + 3) * 2 + "-" * 8)

            if self.aiboard.live_ships == 0:
                print("-" * (4 * self.size + 3) * 2 + "-" * 8)
                print("Игрок выиграл, поздравляем!")
                print(self)
                break

            if self.userboard.live_ships == 0:
                print("-" * (4 * self.size + 3) * 2 + "-" * 8)
                print("Компьютер выиграл!")
                print(self)
                break

            if repeat:
                continue
            num += 1

    def start(self):
        self.greet()
        self.loop()


if __name__ == "__main__":
#Создается игра, указан размер поля и список длин кораблей
    g = Game(9, [4, 3, 3, 2, 2, 2, 1, 1, 1, 1])
    g.start()
