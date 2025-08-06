

from common import draw_texture, load_texture


class Weapon:
    def __init__(self) -> None:
        self.__texture_id, self.__width, self.__height = load_texture("image/weapon3-gimp.png")

    def draw(self, x: float, y: float):
        draw_texture(self.__texture_id, x, y, self.__width, self.__height)
