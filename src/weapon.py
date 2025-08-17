

from common import load_texture
from renderer import Renderer


class Weapon:
    def __init__(self, renderer: Renderer) -> None:
        self.__texture_id, self.__width, self.__height = load_texture("image/weapon3-gimp.png")
        self.__renderer = renderer

    def draw(self, x: float, y: float):
        self.__renderer.add_texture_quad(self.__texture_id, x, y, self.__width, self.__height)
