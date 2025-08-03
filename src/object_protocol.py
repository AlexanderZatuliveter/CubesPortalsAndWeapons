from typing import Protocol

import pygame


class ObjectProtocol(Protocol):
    rect: pygame.Rect
    speed: float  
    velocity_y: float
    max_velocity_y: float
