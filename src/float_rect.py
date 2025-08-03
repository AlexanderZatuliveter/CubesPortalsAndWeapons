from typing import Iterator, Tuple


class FloatRect:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def __repr__(self):
        return f"<FloatRect({self.x}, {self.y}, {self.width}, {self.height})>"

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y, self.width, self.height))

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y, self.width, self.height)[index]

    def __len__(self) -> int:
        return 4

    def copy(self) -> "FloatRect":
        return FloatRect(self.x, self.y, self.width, self.height)

    @property
    def left(self) -> float:
        return self.x

    @left.setter
    def left(self, value: float) -> None:
        self.x = float(value)

    @property
    def right(self) -> float:
        return self.x + self.width

    @right.setter
    def right(self, value: float) -> None:
        self.x = float(value) - self.width

    @property
    def top(self) -> float:
        return self.y

    @top.setter
    def top(self, value: float) -> None:
        self.y = float(value)

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @bottom.setter
    def bottom(self, value: float) -> None:
        self.y = float(value) - self.height

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    @property
    def centerx(self) -> float:
        return self.x + self.width / 2

    @property
    def centery(self) -> float:
        return self.y + self.height / 2

    @property
    def size(self) -> Tuple[float, float]:
        return (self.width, self.height)

    @property
    def topleft(self) -> Tuple[float, float]:
        return (self.left, self.top)

    @property
    def bottomright(self) -> Tuple[float, float]:
        return (self.right, self.bottom)

    @property
    def bottomleft(self) -> Tuple[float, float]:
        return (self.left, self.bottom)

    @property
    def midtop(self) -> Tuple[float, float]:
        return (self.centerx, self.top)

    @property
    def midbottom(self) -> Tuple[float, float]:
        return (self.centerx, self.bottom)

    @property
    def midleft(self) -> Tuple[float, float]:
        return (self.left, self.centery)

    @property
    def midright(self) -> Tuple[float, float]:
        return (self.right, self.centery)

    @property
    def w(self) -> float:
        return self.width

    @property
    def h(self) -> float:
        return self.height

    # Collision
    def collidepoint(self, px: float, py: float) -> bool:
        return self.left <= px < self.right and self.top <= py < self.bottom

    def colliderect(self, other: "FloatRect") -> bool:
        return not (
            self.right <= other.left or
            self.left >= other.right or
            self.bottom <= other.top or
            self.top >= other.bottom
        )

    # Movement
    def move(self, dx: float, dy: float) -> "FloatRect":
        return FloatRect(self.x + dx, self.y + dy, self.width, self.height)

    def move_ip(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    # Inflate
    def inflate(self, dx: float, dy: float) -> "FloatRect":
        return FloatRect(
            self.x - dx / 2,
            self.y - dy / 2,
            self.width + dx,
            self.height + dy
        )

    def inflate_ip(self, dx: float, dy: float) -> None:
        self.x -= dx / 2
        self.y -= dy / 2
        self.width += dx
        self.height += dy

    # Update
    def update(self, x: float, y: float, width: float, height: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
