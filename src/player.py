import pygame
from pygame.key import ScancodeWrapper
from OpenGL.GL import *  # type: ignore
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, IS_DEBUG, PLAYER_JUMP_FORCE, PLAYER_SPEED, GRAVITY
from game_field import GameField
from physics import Physics


class Player:
    def __init__(self, game_field: GameField) -> None:
        size = BLOCK_SIZE
        start_pos = GAME_FIELD_WIDTH // 3, GAME_FIELD_HEIGHT - BLOCK_SIZE * 2
        self.rect = pygame.Rect(*start_pos, size, size)
        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)

        self.velocity_y = 0
        self.max_velocity_y = 50
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.speed = PLAYER_SPEED

    def update(self, keys: ScancodeWrapper) -> None:

        if keys[pygame.K_a] and not self.__physics.is_block(direction="left"):
            self.rect.centerx -= PLAYER_SPEED

        if keys[pygame.K_d] and not self.__physics.is_block(direction="right"):
            self.rect.centerx += PLAYER_SPEED

        is_bottom_block = self.__physics.is_block(direction="bottom")
        is_upper_block = self.__physics.is_block(direction="top")

        if keys[pygame.K_w] and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force

        self.__physics.gravitation()
        self.__physics.borders_teleportation()

    def __draw_square(self, x: int, y: int, color: tuple[float, float, float] = (1, 0, 0), size: int = 4) -> None:
        half = size / 2
        glColor3f(color[0], color[1], color[2])
        glVertex2f(x - half, y - half)
        glVertex2f(x + half, y - half)
        glVertex2f(x + half, y + half)
        glVertex2f(x - half, y + half)

    def draw(self) -> None:

        if IS_DEBUG:
            glColor3f(1, 1, 0)
            glVertex2f(self.rect.x - 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y - 1)
            glVertex2f(self.rect.x + self.rect.w + 1, self.rect.y + self.rect.h + 1)
            glVertex2f(self.rect.x - 1, self.rect.y + self.rect.h + 1)

            self.__draw_square(self.rect.x, self.rect.y, (0 / 255, 255 / 255, 0 / 255))

            rx, ry1, ry2 = self.__physics.collidepoints("right")
            self.__draw_square(rx, ry1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(rx, ry2, (255 / 255, 123 / 255, 0 / 255))

            lx, ly1, ly2 = self.__physics.collidepoints("left")
            self.__draw_square(lx, ly1, (255 / 255, 123 / 255, 0 / 255))
            self.__draw_square(lx, ly2, (255 / 255, 123 / 255, 0 / 255))

            tx1, tx2, ty = self.__physics.collidepoints("top")
            self.__draw_square(tx1, ty)
            self.__draw_square(tx2, ty)

            bx1, bx2, by = self.__physics.collidepoints("bottom")
            self.__draw_square(bx1, by)
            self.__draw_square(bx2, by)

        glColor3f(50 / 255, 50 / 255, 235 / 255)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y)
        glVertex2f(self.rect.x + self.rect.w, self.rect.y + self.rect.h)
        glVertex2f(self.rect.x, self.rect.y + self.rect.h)
