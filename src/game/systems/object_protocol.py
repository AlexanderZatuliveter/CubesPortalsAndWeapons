from typing import Protocol
from game.entities.bullet import Bullet
from game.systems.float_rect import FloatRect


class ObjectProtocol(Protocol):
    rect: FloatRect
    speed: float
    velocity_y: float
    max_velocity_y: float
    anti_gravity: float


class DamageableObject(Protocol):
    rect: FloatRect
    _color: tuple[float, float, float, float]
    _is_endless_health: bool
    _is_strength_increase: bool
    def damage(self, bullet: Bullet) -> None | str: ...
    def add_score(self) -> None: ...
    def kill(self) -> None: ...
