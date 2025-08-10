from typing import Protocol
from float_rect import FloatRect


class ObjectProtocol(Protocol):
    rect: FloatRect
    speed: float
    velocity_y: float
    max_velocity_y: float
    anti_gravity: float
