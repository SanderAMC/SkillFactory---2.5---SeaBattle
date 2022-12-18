import random

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
        return f"Point({self.x}, {self.y})"

class Ship():
    def __init__(self, cone, length, direct):
        self.length = length
        self.point = cone
        self.dir = direct
        self.lives = length

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

    def isshooten(self, point):
        return (point in self.shipdots)

class Board():
    def __init__(self, size, hide = False):
        self.boardsize = size
        self.hide = hide
        self.hitships = 0

        self.board = [["_"]*self.boardsize for _ in range(self.boardsize) ]

        self.busydots = []
        self.ships = []

        self.live_ships = 0

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

    def contour(self, ship, verb = False):
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

    def isoutboard(self, point):
        return not (0 <= point.x < self.boardsize and 0 <= point.y < self.boardsize)

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
                    print("Корабль ранен!")
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

    def ask(self):
        self.get_pref_moves()
#        print("Желательные ходы компа ", self.pref_moves)

        if len(self.pref_moves) > 0:
            d = random.choice(self.pref_moves)
        else:
            self.get_free_moves()
            d = random.choice(self.pref_moves)

        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

    def get_pref_moves(self):
        self.pref_moves = []
        pref = [ (-1, 0), (0, -1), (0, 1), (1, 0) ]

        for x in range(self.enemy_board.boardsize):
            for y in range(self.enemy_board.boardsize):
                if self.enemy_board.board[x][y] == "X":
                    for dx, dy in pref:
                        cur = Dot(x + dx, y + dy)
                        if not (self.enemy_board.isoutboard(cur)) and cur not in self.enemy_board.busydots:
                            self.pref_moves.append(cur)

        return

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
            cords = input("Ваш ход: ").split()

            if len(cords) < 2 or not cords[0].isdigit() or not cords[1].isdigit() or int(cords[0]) > self.enemy_board.boardsize or int(cords[1]) > self.enemy_board.boardsize:
                print("Не ошибайтесь при вводе.")
                continue

            return Dot(int(cords[0]) - 1, int(cords[1]) - 1)

class Game():

    def __init__(self, size, ships):
        self.size = size
        self.squadron = ships
        self.userboard = self.randomboard()
        self.aiboard = self.randomboard()
        self.aiboard.hide = True
        self.User = User(self.aiboard)
        self.Ai = Ai_Player(self.userboard)
        pass

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

    def fillboard(self):
        lens = self.squadron
        board = Board(self.size)

        for l in lens:

            attempts = 0
            while True:
                if attempts > 2000:
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
        print("Морской бой. х - строка, у - столбец")

    def loop(self):
        num = 0
        while True:
            print(self)

            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.User.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.Ai.move()

            print(f"У игрока осталось {self.userboard.live_ships} подбито {self.userboard.hitships}, у компа осталось {self.aiboard.live_ships} подбито {self.aiboard.hitships}.")

            if self.aiboard.hitships == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                print(self)
                break

            if self.userboard.hitships == 7:
                print("-" * 20)
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

    g = Game(9, [3, 2, 2, 1, 1, 1, 1])
    g.start()
