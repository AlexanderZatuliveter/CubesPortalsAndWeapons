import numpy
import pygame
from OpenGL.GL import *  # type: ignore
from bullet import Bullet
from bullets import Bullets
from consts import BLOCK_SIZE, BULLET_DAMAGE, BULLET_HEIGHT, BULLET_WIDTH, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, CHANGE_ANTI_GRAVITY, PLAYER_HEALTH, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_SPEED
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics
from pygame.event import Event


class Player:
    def __init__(
        self,
        game_field: GameField,
        shader,
        color: tuple[float, float, float],
        joystick_num: int,
        bullets: Bullets
    ) -> None:

        self.rect = FloatRect(GAME_FIELD_WIDTH // 3, GAME_FIELD_HEIGHT - BLOCK_SIZE * 2 - 10.0, BLOCK_SIZE, BLOCK_SIZE)
        self.__joystick = pygame.joystick.Joystick(joystick_num)
        self.__color = color
        self.__health = PLAYER_HEALTH
        self.__direction = DirectionEnum.LEFT

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)
        self.__bullets = bullets

        self.velocity_y = 0.0
        self.max_velocity_y = 25.0
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__jumping = False

        self.__shader = shader
        self.__uPlayerPos = glGetUniformLocation(self.__shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(self.__shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(self.__shader, "uColor")

        vertices = numpy.array([
            0.0, 0.0,
            BLOCK_SIZE, 0.0,
            BLOCK_SIZE, BLOCK_SIZE,
            0.0, BLOCK_SIZE,
        ], dtype=numpy.float32)

        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    def damage(self):
        self.__health -= BULLET_DAMAGE

        if self.__health <= 0.0:
            print("player dead!")

    def update(self, events: list[Event]) -> None:

        # left stick x
        axis_x = self.__joystick.get_axis(0)

        dead_zone = 0.3
        if abs(axis_x) < dead_zone:
            axis_x = 0

        difx = axis_x * self.speed

        is_block = self.__physics.side_blocks()

        if difx > 0:
            self.__direction = DirectionEnum.RIGHT
        elif difx < 0:
            self.__direction = DirectionEnum.LEFT

        if is_block is None:
            self.rect.x += difx
        else:
            # is_block = right
            if difx > 0 and is_block != DirectionEnum.RIGHT:
                self.rect.x += difx
            elif difx < 0 and is_block == DirectionEnum.RIGHT:
                self.rect.x += difx
            # is_block = left
            if difx < 0 and is_block != DirectionEnum.LEFT:
                self.rect.x += difx
            elif difx > 0 and is_block == DirectionEnum.LEFT:
                self.rect.x += difx

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP)

        if self.__joystick.get_button(0) and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force
            self.__jumping = True

        if not self.__joystick.get_button(0):
            self.__jumping = False
            self.anti_gravity = 0

        if self.__jumping and self.__joystick.get_button(0) and self.velocity_y < 0:
            if self.anti_gravity < self.__max_anti_gravity:
                self.anti_gravity += self.__change_anti_gravity

        if self.__jumping == True and self.anti_gravity > 0:
            self.anti_gravity -= 0.005

        self.__physics.gravitation()
        self.__physics.side_blocks()
        self.__physics.borders_teleportation()

        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:

                    if self.__direction == DirectionEnum.RIGHT:
                        x = self.rect.x + self.rect.width
                    else:
                        x = self.rect.x - BULLET_WIDTH

                    self.__bullets.add_bullet(Bullet(
                        x,
                        self.rect.y + self.rect.height / 2 - BULLET_HEIGHT / 2,
                        self.__direction,
                        self.__shader
                    ))

    def draw(self) -> None:
        glBindVertexArray(self.__vao)
        glUniform1i(self.__uIsPlayer, 1)
        glUniform2f(self.__uPlayerPos, self.rect.x, self.rect.y)
        glUniform3f(self.__uColor, *self.__color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)
