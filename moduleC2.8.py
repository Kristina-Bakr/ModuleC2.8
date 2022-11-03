from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, o, l, bow):
        self.l = l
        self.lives = l
        self.bow = bow
        self.o = o

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.o.x
            cur_y = self.o.y

            if self.bow == 0:
                cur_x += i

            elif self.bow == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


class Field:
    def __init__(self, hid = False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field1 = [["0"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field1):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field1[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field1[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field1[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль ранен")
                    return True

        self.field1[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class PC(Player):
    def ask(self):
        dots = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dots.x + 1} {dots.y + 1}")
        return dots


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа ")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        player = self.random_field()
        pc = self.random_field()
        pc.hid = True

        self.pc = PC(pc, player)
        self.player = User(player, pc)

    def try_field(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = Field(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    field.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        field.begin()
        return field

    def random_field(self):
        field = None
        while field is None:
            field = self.try_field()
        return field

    def greet(self):
        print(" формат ввода: x и y, где ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.player.field)
            print("-" * 20)
            print("Доска ПК:")
            print(self.pc.field)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит игрока!")
                repeat = self.player.move()
            else:
                print("Ходит ПК!")
                repeat = self.pc.move()
            if repeat:
                num -= 1

            if self.pc.field.count == 7:
                print("-" * 20)
                print("игрок выиграл!")
                break

            if self.player.field.count == 7:
                print("-" * 20)
                print("ПК выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()