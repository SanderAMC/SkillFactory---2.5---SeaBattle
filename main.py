import random

class BoardExceptions(Exception):
    def __str__(self):
        return "Какой-то exception"

class BoardOutException(BoardExceptions):
    def __str__(self):
        return "Выстрел мимо доски"

class BoardAlreadyException(BoardExceptions):
    def __str__(self):
        return "Уже стреляли сюда"

class BoardShipPlaceException(BoardExceptions):
    def __str__(self):
        return "Что-то не так с размещением корабля"

class Dot():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Ship():
    def __init__(self, p, l, d):
        self.length = l
        self.point = p
        self.dir = d
        self.lives = l

    @property
    def ShipDots(self):
        dots = []
        x_ = self.point.x
        y_ = self.point.y
        for _ in range(self.length):
            d = Dot(x_, y_)
            dots.append(d)

            if self.dir == 0:
                x_ += 1
            else:
                y_ += 1

        return dots

    def IsShooten(self, p):
        return (p in self.ShipDots)

class Board():
    def __init__(self, l = 6, h = False):
        self.boardsize = l
        self.hide = h
        self.hitships = 0

        self.board = [["_"]*self.boardsize for _ in range(self.boardsize) ]

        self.busydots = []
        self.ships = []

        self.live_ships = 0

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.board):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("█", "_")
        return res

    def Add_Ship(self, ship):
        for d in ship.ShipDots:
            if self.IsOutBoard(d) or d in self.busydots:
                raise BoardShipPlaceException
        for d in ship.ShipDots:
            self.board[d.x][d.y] = "█"
            self.busydots.append(d)

        self.live_ships += 1
        self.ships.append(ship)
        self.Contour(ship)

    def Contour(self, ship, verb = False):

        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.ShipDots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)

                if not (self.IsOutBoard(cur)) and cur not in self.busydots:
                    if verb:
                        self.board[cur.x][cur.y] = "∙"
                    self.busydots.append(cur)


    def Show_Board(self):
        pass

    def IsOutBoard(self, point):
        return not (0 <= point.x < self.boardsize and 0 <= point.y < self.boardsize)

    def shot(self, point):
        if self.IsOutBoard(point):
            raise BoardOutException()

        if point in self.busydots:
            raise BoardAlreadyException()

        self.busydots.append(point)

        for ship in self.ships:
            if ship.IsShooten(point):
                ship.lives -= 1
                self.board[point.x][point.y] = "X"
                if ship.lives == 0:
                    self.hitships += 1
                    self.live_ships -= 1
                    self.Contour(ship, verb=True)
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
#        self.my_board = my_board
        self.enemy_board = enemy_board

    def Ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                return self.enemy_board.shot(self.Ask())
            except BoardAlreadyException as e:
                print(e)

class Ai_Player(Player):
    def Ask(self):
        d = Dot(random.randint(0,5), random.randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def Ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) < 2 or not cords[0].isdigit() or not cords[1].isdigit() or int(cords[0]) > 6 or int(cords[1]) > 6:
                print("Не ошибайтесь при вводе.")
                continue

            return Dot(int(cords[0]) - 1, int(cords[1]) - 1)

class Game():

    def __init__(self):
        self.size = 6
        self.userboard = self.RandomBoard()
        self.aiboard = self.RandomBoard()
        self.aiboard.hide = True
        self.User = User(self.aiboard)
        self.Ai = Ai_Player(self.userboard)
        pass

    def RandomBoard(self):
        board = None
        while board is None:
            board = self.FillBoard()
        return board
    def FillBoard(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
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
                    board.Add_Ship(ship)
                    break
                except BoardShipPlaceException:
                    attempts += 1
                    pass

        board.begin()
        return board

    def Greet(self):
        print("Морской бой. х - строка, у - столбец")

    def Loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.userboard)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.aiboard)

            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.User.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.Ai.move()

            print(f"У игрока осталось {self.userboard.live_ships} подбито {self.userboard.hitships}, у компа осталось {self.aiboard.live_ships} подбито {self.aiboard.hitships}.")
            print("Продолжение хода ", repeat)

            if self.aiboard.hitships == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.userboard.hitships == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break

            if repeat:
                continue
            num += 1


    def Start(self):
        self.Greet()
        self.Loop()


if __name__ == "__main__":

    g = Game()
    g.Start()
