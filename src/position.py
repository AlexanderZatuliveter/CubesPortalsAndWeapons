
from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float


@dataclass
class IntPosition:
    x: int
    y: int

    def __str__(self):
        return f"{self.x}x{self.y}"

    @classmethod
    def from_string(cls, position_str: str):
        try:
            x_str, y_str = position_str.split('x')
            x = int(x_str)
            y = int(y_str)
            return cls(x, y)
        except ValueError:
            raise ValueError(f"Invalid position string format: '{position_str}'")