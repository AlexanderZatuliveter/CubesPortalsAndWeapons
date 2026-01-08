
import random
from OpenGL.GL.shaders import ShaderProgram
import numpy as np

from engine.graphics.opengl_3d_utils import OpenGL_3D_Utils
from game.consts import BLOCK_SIZE
from game.entities.weapon import Weapon
from game.enums.weapon_enum import WeaponEnum
from game.game_field import GameField


class Weapons(list[Weapon]):
    def __init__(self, game_field: GameField, shader: ShaderProgram | None) -> None:
        self.__shader = shader

        self.__weapons = {
            WeaponEnum.BAZOOKA: OpenGL_3D_Utils.load("src/_content/3D_models/bazooka.STL"),
            WeaponEnum.MACHINE_GUN: OpenGL_3D_Utils.load("src/_content/3D_models/machine_gun.STL"),
            WeaponEnum.SHOTGUN: OpenGL_3D_Utils.load("src/_content/3D_models/shotgun.STL")
        }

        none_positions, block_positions = game_field.return_block_positions()

        if block_positions:
            for num in range(5):
                while True:
                    new_weapon = self.__create_weapon(
                        block_positions,
                        none_positions
                    )

                    invalid = False

                    for weapon in self:
                        if new_weapon.rect.colliderect(weapon.rect):
                            invalid = True
                            break

                    if invalid:
                        continue

                    self.append(new_weapon)
                    break

    def __create_weapon(
        self,
        block_positions: list[tuple[int, int]],
        none_positions: list[tuple[int, int]]
    ) -> Weapon:

        model = random.choice(list(self.__weapons.keys()))

        while True:
            weapon_pos = random.choice(none_positions)

            if (weapon_pos[0], weapon_pos[1] + BLOCK_SIZE) not in block_positions:
                continue
            if (weapon_pos[0], weapon_pos[1] - BLOCK_SIZE) in block_positions \
                    or (weapon_pos[0] + BLOCK_SIZE, weapon_pos[1] - BLOCK_SIZE) in block_positions:
                continue
            if (weapon_pos[0] + BLOCK_SIZE, weapon_pos[1]) in block_positions:
                continue

            break

        return Weapon(self.__shader, weapon_pos, model, self.__weapons[model])

    def draw(self, projection: 'np.ndarray', view: 'np.ndarray', t: float,
             light_pos: 'np.ndarray', camera_pos: 'np.ndarray') -> None:
        for weapon in self:
            weapon.draw(projection, view, t, light_pos, camera_pos)
