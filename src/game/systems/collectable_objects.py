import numpy as np
import random

from OpenGL.GL.shaders import ShaderProgram
import pygame
from engine.graphics.opengl_3d_utils import OpenGL_3D_Utils
from game.consts import BLOCK_SIZE
from game.game_field import GameField
from game.entities.buff import Buff
from game.entities.weapon import Weapon
from game.enums.buff_enum import BuffEnum
from game.enums.weapon_enum import WeaponEnum


class CollectableObjects(list[Buff | Weapon]):

    def __init__(self, game_field: GameField, shader: ShaderProgram | None) -> None:
        super().__init__()
        self.__shader = shader

        self.__none_positions, self.__block_positions = game_field.return_block_positions()

        if not self.__block_positions:
            return

        # Конфиги для разных типов предметов
        self.__buffs_config = {
            BuffEnum.ENDLESS_HEALTH: "src/_content/3D_models/buffs/heart.STL",
            BuffEnum.STRENGTH_INCREASE: "src/_content/3D_models/buffs/energy_drink.STL"
        }

        self.__weapons_config = {
            WeaponEnum.BAZOOKA: "src/_content/3D_models/weapons/bazooka.STL",
            WeaponEnum.MACHINE_GUN: "src/_content/3D_models/weapons/machine_gun.STL",
            WeaponEnum.SHOTGUN: "src/_content/3D_models/weapons/shotgun.STL"
        }

        # Загружаем модели
        self.__buff_models = {
            enum_val: OpenGL_3D_Utils.load(path)
            for enum_val, path in self.__buffs_config.items()
        }

        self.__weapons_models = {
            enum_val: OpenGL_3D_Utils.load(path)
            for enum_val, path in self.__weapons_config.items()
        }

        self.__buff_timer = 0
        self.__weapon_timer = 0
        self.__timers_cooldown = 10000

    def update(self) -> None:
        if self.__buff_timer == 0:
            while True:
                buff = self.__create_item(
                    self.__buff_models,
                    Buff,
                    self.__block_positions,
                    self.__none_positions
                )

                if not self.__check_collision(buff):
                    self.append(buff)
                    break

            self.__buff_timer = pygame.time.get_ticks()

        if self.__weapon_timer == 0:
            for _ in range(2):
                while True:
                    weapon = self.__create_item(
                        self.__weapons_models,
                        Weapon,
                        self.__block_positions,
                        self.__none_positions
                    )

                    if not self.__check_collision(weapon):
                        self.append(weapon)
                        break

            self.__weapon_timer = pygame.time.get_ticks()

        if len(self) > 6:
            return

        if pygame.time.get_ticks() - self.__buff_timer >= self.__timers_cooldown:
            self.__buff_timer = 0
        if pygame.time.get_ticks() - self.__weapon_timer >= self.__timers_cooldown:
            self.__weapon_timer = 0

    def __create_item(
        self,
        models: dict,
        item_class,
        block_positions: list[tuple[int, int]],
        none_positions: list[tuple[int, int]]
    ):
        model_enum = random.choice(list(models.keys()))

        while True:
            item_pos = random.choice(none_positions)

            if (item_pos[0], item_pos[1] + BLOCK_SIZE) not in block_positions:
                continue
            if (item_pos[0], item_pos[1] - BLOCK_SIZE) in block_positions:
                continue
            if item_pos in block_positions:
                continue

            break

        return item_class(self.__shader, item_pos, model_enum, models[model_enum])

    def __check_collision(self, item) -> bool:
        for existing_item in self:
            if item.rect.colliderect(existing_item.rect):
                return True
        return False

    def draw(
        self,
        projection: np.ndarray,
        view: np.ndarray,
        t: float,
        light_pos: np.ndarray,
        camera_pos: np.ndarray,
        uniforms: dict
    ) -> None:
        for item in self:
            item.draw(projection, view, t, light_pos, camera_pos, uniforms)
