
import pygame
from OpenGL.GL import *  # type: ignore
import ctypes

from game.entities.bullet import Bullet
from game.enums.buff_enum import BuffEnum
from game.enums.weapon_enum import WeaponEnum
from game.systems.bullets import Bullets
from game.consts import ANTI_GRAVITY_DECAY, BAZOOKA_BULLET_HEIGHT, BAZOOKA_BULLET_WIDTH, BAZOOKA_COOLDOWN, BLOCK_SIZE, BUFF_COOLDOWN, CHANGE_ANTI_GRAVITY, MACHINE_GUN_BULLET_HEIGHT, MACHINE_GUN_BULLET_WIDTH, MACHINE_GUN_COOLDOWN, PISTOL_BULLET_HEIGHT, PISTOL_BULLET_WIDTH, PISTOL_COOLDOWN, PLAYER_DASH_DURATION, PLAYER_DASH_SPEED, PLAYER_HEALTH, PLAYER_JUMP_FORCE, MAX_ANTI_GRAVITY, PLAYER_MAX_VELOCITY_Y, PLAYER_SPEED, SHOTGUN_BULLET_HEIGHT, SHOTGUN_BULLET_WIDTH, SHOTGUN_COOLDOWN
from game.enums.direction_enum import DirectionEnum
from game.systems.float_rect import FloatRect
from game.game_field import GameField
from engine.graphics.opengl_utils import OpenGLUtils
from game.systems.physics import Physics
from engine.graphics.renderer_2d import Renderer2D
from game.systems.scores import Scores


class Player:
    def __init__(
        self,
        game_field: GameField,
        shader,
        start_pos: tuple[float, float],
        color: tuple[float, float, float, float],
        bullets: Bullets
    ) -> None:

        self.__start_pos = start_pos
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

        self.__is_dashing = False
        self.__dash_duration = PLAYER_DASH_DURATION
        self.__dash_speed = PLAYER_DASH_SPEED
        self.__dash_start_time = 0
        self.__dash_last_time = 0

        self._is_endless_health = False
        self.__endless_health_start = 0
        self._is_strength_increase = False
        self.__strength_increase_start = 0

        self.__default_weapon = WeaponEnum.PISTOL
        self.update_weapon(self.__default_weapon)

        self._shot_time = 0
        self._is_shot = False

        self.__shader = shader
        self.__renderer = Renderer2D()

        self.__uPlayerPos = glGetUniformLocation(self.__shader, "uPlayerPos")
        self.__uIsPlayer = glGetUniformLocation(self.__shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(self.__shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(self.__shader, "uUseTexture")

        self.__vao, self.__vbo = self.__create_vao_vbo(BLOCK_SIZE)
        self.__health_vao, self.__health_vbo = self.__create_vao_vbo(BLOCK_SIZE)

        self.__last_health = self.__health

    def __create_vao_vbo(self, size: float):
        vertices = OpenGLUtils.create_square_vertices(size)
        self.__vertex_count = 4
        vao, vbo = self.__renderer.create_vao_vbo(vertices)

        # Configure vertex attribute for position (aPos at location 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        return vao, vbo

    def update_weapon(self, weapon_type: WeaponEnum):
        self.__current_weapon = weapon_type

        if self.__current_weapon == WeaponEnum.PISTOL:
            self._shot_cooldown = PISTOL_COOLDOWN
            self.__bullet_width, self.__bullet_height = PISTOL_BULLET_WIDTH, PISTOL_BULLET_HEIGHT
        elif self.__current_weapon == WeaponEnum.MACHINE_GUN:
            self._shot_cooldown = MACHINE_GUN_COOLDOWN
            self.__bullet_width, self.__bullet_height = MACHINE_GUN_BULLET_WIDTH, MACHINE_GUN_BULLET_HEIGHT
        elif self.__current_weapon == WeaponEnum.BAZOOKA:
            self._shot_cooldown = BAZOOKA_COOLDOWN
            self.__bullet_width, self.__bullet_height = BAZOOKA_BULLET_WIDTH, BAZOOKA_BULLET_HEIGHT
        elif self.__current_weapon == WeaponEnum.SHOTGUN:
            self._shot_cooldown = SHOTGUN_COOLDOWN
            self.__bullet_width, self.__bullet_height = SHOTGUN_BULLET_WIDTH, SHOTGUN_BULLET_HEIGHT

    def damage(self, bullet: Bullet):
        if not self._is_endless_health:
            self.__health -= bullet.damage

        if self.__joystick:
            if bullet._type == WeaponEnum.MACHINE_GUN:
                self.__joystick.rumble(0.0, 0.3, 100)
            if bullet._type == WeaponEnum.SHOTGUN:
                self.__joystick.rumble(0.1, 0.3, 100)
            if bullet._type == WeaponEnum.BAZOOKA:
                self.__joystick.rumble(0.2, 0.4, 150)

        if self.__health <= 0:
            self.rect = FloatRect(*self.__start_pos, BLOCK_SIZE, BLOCK_SIZE)
            self.__health = PLAYER_HEALTH
            self.__bullets.clear_by_color(self._color)
            self.__health_vao, self.__health_vbo = self.__create_vao_vbo(BLOCK_SIZE)
            self.__current_weapon = self.__default_weapon
            return "kill"

    def kill(self) -> None:
        self.remove_score()
        self.rect = FloatRect(*self.__start_pos, BLOCK_SIZE, BLOCK_SIZE)
        self.__health = PLAYER_HEALTH
        self.__bullets.clear_by_color(self._color)
        self.__health_vao, self.__health_vbo = self.__create_vao_vbo(BLOCK_SIZE)
        self.__current_weapon = self.__default_weapon

    def __shoot(self) -> None:

        if not self.__joystick:
            return

        # попытка выстрела
        if self.__direction == DirectionEnum.RIGHT:
            x = self.rect.x + self.rect.width
        else:
            x = self.rect.x - self.__bullet_width

        if self._is_strength_increase:
            damage_coefficient = 1.5
        else:
            damage_coefficient = 1.0

        if self.__current_weapon == WeaponEnum.SHOTGUN:
            angles = [15, 0, -15]
            for num in range(3):
                self.__bullets.add_bullet(Bullet(
                    x,
                    self.rect.y + self.rect.height / 2 - self.__bullet_height / 2,
                    self.__direction,
                    self._color,
                    self.__shader,
                    self.__current_weapon,
                    angle=angles[num],
                    damage_coefficient=damage_coefficient
                ))
        else:
            self.__bullets.add_bullet(Bullet(
                x,
                self.rect.y + self.rect.height / 2 - self.__bullet_height / 2,
                self.__direction,
                self._color,
                self.__shader,
                self.__current_weapon,
                damage_coefficient=damage_coefficient
            ))

        self._is_shot = True
        self._shot_time = pygame.time.get_ticks()

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

        # Right and left movement
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

        # Dash
        current_time = pygame.time.get_ticks()

        if current_time - self.__dash_last_time > 1000 and not self.__is_dashing:
            if self.__joystick and self.__joystick.get_button(2):
                self.__is_dashing = True
                self.__dash_start_time = current_time
                self.__dash_last_time = current_time

        if self.__is_dashing:
            if current_time - self.__dash_start_time < self.__dash_duration:
                if self.__direction == DirectionEnum.RIGHT:
                    self.rect.x += self.__dash_speed * dt
                else:
                    self.rect.x -= self.__dash_speed * dt
            else:
                self.__is_dashing = False

        is_bottom_block = self.__physics.is_block(DirectionEnum.DOWN, dt)
        is_upper_block = self.__physics.is_block(DirectionEnum.UP, dt)
        is_left_block = self.__physics.is_block(DirectionEnum.LEFT, dt)
        is_right_block = self.__physics.is_block(DirectionEnum.RIGHT, dt)

        if self.__joystick and self.__joystick.get_button(0) \
                and (is_bottom_block or is_left_block or is_right_block) and not is_upper_block:
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

        # Physics
        self.__physics.gravitation(dt)

        # Bullets
        if not self.__joystick:
            return

        if not self._is_shot:
            if self.__joystick.get_axis(5) > 0:
                self.__shoot()

        if self._is_shot and pygame.time.get_ticks() - self._shot_time >= self._shot_cooldown:
            self._is_shot = False
            self._shot_time = 0

        if self._is_endless_health and pygame.time.get_ticks() - self.__endless_health_start >= BUFF_COOLDOWN:
            self._is_endless_health = False
            self.__endless_health_start = 0

        if self._is_strength_increase and pygame.time.get_ticks() - self.__strength_increase_start >= BUFF_COOLDOWN:
            self._is_strength_increase = False
            self.__strength_increase_start = 0

        # Update scores
        self.__draw_scores.update_pos(self.rect.x, self.rect.y - BLOCK_SIZE * 1.01)

    def draw(self) -> None:
        self.__draw_scores.draw()

        health = self.__health / PLAYER_HEALTH
        size = self.rect.w * health
        rect = FloatRect(self.rect.x + (self.rect.w - size) / 2, self.rect.y + (self.rect.h - size) / 2, size, size)

        if self.__last_health != self.__health:
            self.__health_vao, self.__health_vbo = self.__create_vao_vbo(size)

        self.__renderer.draw_rect(
            self.__health_vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, rect, self._color,
            self.__vertex_count
        )

        blur_color = (self._color[0], self._color[1], self._color[2], 0.4)

        self.__renderer.draw_rect(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, True), self.__uPlayerPos,
            self.__uColor, self.rect, blur_color,
            self.__vertex_count
        )

    def get_joystick(self) -> pygame.joystick.JoystickType | None:
        return self.__joystick

    def set_joystick(self, joystick: pygame.joystick.JoystickType):
        self.__joystick = joystick

    def add_score(self) -> None:
        self.__scores += 1
        self.__draw_scores.update_text(str(self.__scores))

    def remove_score(self) -> None:
        if self.__scores > 0:
            self.__scores -= 1
            self.__draw_scores.update_text(str(self.__scores))

    def get_scores(self) -> int:
        return self.__scores

    def set_buff(self, buff_type: BuffEnum) -> None:
        if buff_type == BuffEnum.ENDLESS_HEALTH:
            self._is_endless_health = True
            self.__endless_health_start = pygame.time.get_ticks()
        elif buff_type == BuffEnum.STRENGTH_INCREASE:
            self._is_strength_increase = True
            self.__strength_increase_start = pygame.time.get_ticks()
        else:
            return
