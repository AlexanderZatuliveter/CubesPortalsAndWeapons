

from bullet import Bullet


class Bullets:
    def __init__(self):
        self.__bullets: list[Bullet] = []

    def update(self):
        for bullet in self.__bullets:
            if bullet.is_destroyed() == True:
                self.destroy(bullet)
            bullet.update()

    def draw(self):
        for bullet in self.__bullets:
            bullet.draw()

    def destroy(self, bullet: Bullet):
        if bullet in self.__bullets:
            self.__bullets.remove(bullet)

    def add_bullet(self, bullet: Bullet):
        self.__bullets.append(bullet)

    def get_bullets(self):
        return self.__bullets

    def clear_by_color(self, color: tuple[float, float, float]):
        self.__bullets = [b for b in self.__bullets if b.color != color]
