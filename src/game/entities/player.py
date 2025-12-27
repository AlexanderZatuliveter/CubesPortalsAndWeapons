
import pygame
from OpenGL.GL import *  # type: ignore

from game.entities.bullet import Bullet
from game.enums.bullet_enum import BulletEnum
from game.entities.bullets import Bullets
from game.consts import ANTI_GRAVITY_DECAY, BLOCK_SIZE, BIG_BULLET_HEIGHT, BIG_BULLET_WIDTH, GAME_FIELD_HEIGHT, CHANGE_ANTI_GRAVITY, PLAYER_HEALTH, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_MAX_VELOCITY_Y, PLAYER_SPEED, SMALL_BULLET_HEIGHT, SMALL_BULLET_WIDTH
from game.enums.direction_enum import DirectionEnum
from game.systems.float_rect import FloatRect
from game.game_field import GameField
from engine.graphics.opengl_utils import OpenGLUtils
from game.systems.physics import Physics
from engine.graphics.renderer import Renderer
from game.systems.scores import Scores


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
        self.__scores = 0

        self.__game_field = game_field
        self.__physics = Physics(self, self.__game_field)
        self.__bullets = bullets
        self.__draw_scores = Scores(self.rect.x, self.rect.y, str(self.__scores), shader, self._color)

        self.velocity_y = 0.0
        self.max_velocity_y = PLAYER_MAX_VELOCITY_Y
        self.speed = PLAYER_SPEED
        self.anti_gravity = 0.0
        self.__max_anti_gravity = MAX_ANTI_GRAVITY
        self.__change_anti_gravity = CHANGE_ANTI_GRAVITY
        self.__anti_gravity_decay = ANTI_GRAVITY_DECAY
        self.__jump_force = -PLAYER_JUMP_FORCE
        self.__jumping = False

        self._big_shot_cooldown = 1000
        self._big_shot_time = 0
        self._is_big_shot = False

        self._small_shot_cooldown = 350
        self._small_shot_time = 0
        self._is_small_shot = False

        self.__shader = shader
        self.__renderer = Renderer()

        self.__uPlayerPos = glGetUniformLocation(self.__shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(self.__shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(self.__shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(self.__shader, "uUseTexture")

        vertices = OpenGLUtils.create_square_vertices(BLOCK_SIZE)
        self.__vertex_count = 4
        self.__vao, self.__vbo = self.__renderer.create_vao_vbo(vertices)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    def damage(self, bullet: Bullet):
        self.__health -= bullet.damage

        if self.__joystick:
            if bullet._type == BulletEnum.SMALL:
                self.__joystick.rumble(0.0, 0.3, 100)
            if bullet._type == BulletEnum.BIG:
                self.__joystick.rumble(0.2, 0.4, 150)

        if self.__health <= 0:
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
            cooldown_flag = "_is_big_shot"
            cooldown_time = "_big_shot_time"
        else:  # SMALL
            width, height = SMALL_BULLET_WIDTH, SMALL_BULLET_HEIGHT
            cooldown_flag = "_is_small_shot"
            cooldown_time = "_small_shot_time"

        # попытка выстрела
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

    def update(self, dt: float) -> None:

        # left stick x
        axis_x = self.__joystick.get_axis(0) if self.__joystick else 0

        dead_zone = 0.3
        if abs(axis_x) < dead_zone:
            axis_x = 0

        difx = axis_x * self.speed * dt

        is_block = self.__physics.side_blocks(dt)

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

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN, dt)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP, dt)

        if self.__joystick and self.__joystick.get_button(0) and is_bottom_block and not is_upper_block:
            self.velocity_y = self.__jump_force
            self.__jumping = True

        if self.__joystick and not self.__joystick.get_button(0):
            self.__jumping = False
            self.anti_gravity = 0

        if self.__jumping and self.__joystick and self.__joystick.get_button(0) and self.velocity_y < 0:
            if self.anti_gravity < self.__max_anti_gravity:
                self.anti_gravity += self.__change_anti_gravity * dt

        if self.__jumping == True and self.anti_gravity > 0:
            self.anti_gravity -= self.__anti_gravity_decay * dt

        self.__physics.gravitation(dt)
        self.__physics.borders_teleportation()

        if not self.__joystick:
            return

        is_shot = not self._is_big_shot and not self._is_small_shot

        if is_shot:
            if (self.__joystick.get_button(1) or self.__joystick.get_axis(5) > 0):
                self.__shoot(bullet_type=BulletEnum.SMALL)
            elif (self.__joystick.get_button(2) or self.__joystick.get_axis(4) > 0):
                self.__shoot(bullet_type=BulletEnum.BIG)

        if self._is_small_shot and pygame.time.get_ticks() - self._small_shot_time >= self._small_shot_cooldown:
            self._is_small_shot = False
            self._small_shot_time = 0
        if self._is_big_shot and pygame.time.get_ticks() - self._big_shot_time >= self._big_shot_cooldown:
            self._is_big_shot = False
            self._big_shot_time = 0

        self.__draw_scores.update_pos(self.rect.x, self.rect.y - BLOCK_SIZE * 0.9)

    def draw(self) -> None:
        self.__draw_scores.draw()
        self.__renderer.draw_square(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, self.rect, self._color,
            self.__vertex_count
        )

    def get_joystick(self) -> pygame.joystick.JoystickType | None:
        return self.__joystick

    def set_joystick(self, joystick: pygame.joystick.JoystickType):
        self.__joystick = joystick

    def add_score(self) -> None:
        self.__scores += 1
        self.__draw_scores.update_text(str(self.__scores))

    def get_scores(self) -> int:
        return self.__scores
