import numpy
import pygame
from OpenGL.GL import *  # type: ignore
from bullet import Bullet
from bullet_enum import BulletEnum
from bullets import Bullets
from consts import BLOCK_SIZE, BIG_BULLET_HEIGHT, BIG_BULLET_WIDTH, GAME_FIELD_HEIGHT, CHANGE_ANTI_GRAVITY, PLAYER_HEALTH, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_SPEED, SMALL_BULLET_HEIGHT, SMALL_BULLET_WIDTH
from direction_enum import DirectionEnum
from float_rect import FloatRect
from game_field import GameField
from physics import Physics
from scores import Scores


class Player:
    def __init__(
        self,
        game_field: GameField,
        shader,
        color: tuple[float, float, float],
        bullets: Bullets
    ) -> None:

        self.__start_pos = BLOCK_SIZE * 12, GAME_FIELD_HEIGHT - BLOCK_SIZE * 3
        self.rect = FloatRect(*self.__start_pos, BLOCK_SIZE, BLOCK_SIZE)
        self.__joystick: pygame.joystick.JoystickType | None = None
        pygame.joystick.init()
        self._color = color
        self.__health = PLAYER_HEALTH
        self.__direction = DirectionEnum.LEFT
        self.__scores = 24

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)
        self.__bullets = bullets
        self.__draw_scores = Scores(0, -BLOCK_SIZE * 1.85, str(self.__scores), shader, self._color)

        self.velocity_y = 0.0
        self.max_velocity_y = 75.0
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__jumping = False

        self.big_shot_cooldown = 750
        self.big_shot_time = 0
        self.is_big_shot = False

        self.small_shot_cooldown = 250
        self.small_shot_time = 0
        self.is_small_shot = False

        self.__shader = shader
        self.__uPlayerPos = glGetUniformLocation(self.__shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(self.__shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(self.__shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(self.__shader, "uUseTexture")

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

    def damage(self, bullet_damage: int):
        self.__health -= bullet_damage

        if self.__health <= 0.0:
            self.rect = FloatRect(*self.__start_pos, BLOCK_SIZE, BLOCK_SIZE)
            self.__health = PLAYER_HEALTH
            self.__bullets.clear_by_color(self._color)
            return "kill"

    def __shoot(self, bullet_type: BulletEnum):

        if not self.__joystick:
            return

        # параметры для обоих типов
        if bullet_type == BulletEnum.BIG:
            width, height = BIG_BULLET_WIDTH, BIG_BULLET_HEIGHT
            is_pressed = self.__joystick.get_button(2) or self.__joystick.get_axis(4) > 0
            cooldown_flag = "is_big_shot"
            cooldown_time = "big_shot_time"
            cooldown_dif = self.big_shot_cooldown
        else:  # SMALL
            width, height = SMALL_BULLET_WIDTH, SMALL_BULLET_HEIGHT
            is_pressed = self.__joystick.get_button(1) or self.__joystick.get_axis(5) > 0
            cooldown_flag = "is_small_shot"
            cooldown_time = "small_shot_time"
            cooldown_dif = self.small_shot_cooldown

        # текущее состояние
        is_shot = getattr(self, cooldown_flag)
        last_time = getattr(self, cooldown_time)

        # попытка выстрела
        if is_pressed and not is_shot:
            x = (self.rect.x + self.rect.width) if self.__direction == DirectionEnum.RIGHT else (self.rect.x - width)

            self.__bullets.add_bullet(Bullet(
                x,
                self.rect.y + self.rect.height / 2 - height / 2,
                self.__direction,
                self._color,
                self.__shader,
                bullet_type
            ))

            setattr(self, cooldown_flag, True)
            setattr(self, cooldown_time, pygame.time.get_ticks())

        # откат перезарядки
        if is_shot and pygame.time.get_ticks() - last_time >= cooldown_dif:
            setattr(self, cooldown_flag, False)
            setattr(self, cooldown_time, 0)

    def update(self) -> None:

        # left stick x
        axis_x = self.__joystick.get_axis(0) if self.__joystick else 0

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

        if self.__joystick and self.__joystick.get_button(0) and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force
            self.__jumping = True

        if self.__joystick and not self.__joystick.get_button(0):
            self.__jumping = False
            self.anti_gravity = 0

        if self.__jumping and self.__joystick and self.__joystick.get_button(0) and self.velocity_y < 0:
            if self.anti_gravity < self.__max_anti_gravity:
                self.anti_gravity += self.__change_anti_gravity

        if self.__jumping == True and self.anti_gravity > 0:
            self.anti_gravity -= 0.005

        self.__physics.gravitation()
        self.__physics.side_blocks()
        self.__physics.borders_teleportation()

        self.__shoot(bullet_type=BulletEnum.BIG)
        self.__shoot(bullet_type=BulletEnum.SMALL)

    def draw(self) -> None:
        glBindVertexArray(self.__vao)
        glUniform1i(self.__uUseTexture, 0)
        glUniform1i(self.__uIsPlayer, 1)
        glUniform2f(self.__uPlayerPos, self.rect.x, self.rect.y)
        glUniform3f(self.__uColor, *self._color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        self.__draw_scores.draw()
        glBindVertexArray(0)

    def get_joystick(self) -> pygame.joystick.JoystickType | None:
        return self.__joystick

    def set_joystick(self, joystick: pygame.joystick.JoystickType):
        self.__joystick = joystick

    def add_score(self) -> None:
        self.__scores += 1
        self.__draw_scores.update_text(str(self.__scores))

    def get_scores(self) -> int:
        return self.__scores
