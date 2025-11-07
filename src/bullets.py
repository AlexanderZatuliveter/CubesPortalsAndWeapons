

from OpenGL.GL import *  # type: ignore
from bullet import Bullet


class Bullets:
    def __init__(self):
        self.__bullets = []

    def update(self):
        for bullet in self.__bullets:
            if bullet.is_destroyed() == True:
                self.destroy(bullet)
            bullet.update()

    def draw(self):
        for bullet in self.__bullets:
            bullet.draw()

    def destroy(self, bullet: Bullet):
        self.__bullets.remove(bullet)

    def add_bullet(self, bullet: Bullet):
        self.__bullets.append(bullet)

    def get_bullets(self):
        return self.__bullets
