
import random
from OpenGL.GL.shaders import ShaderProgram
import numpy as np

from game.consts import BLOCK_SIZE
from game.entities.weapon import Weapon
from game.enums.weapon_enum import WeaponEnum
from game.game_field import GameField


class Weapons(list[Weapon]):
    def __init__(self, game_field: GameField, shader: ShaderProgram | None, shader_2d: ShaderProgram | None) -> None:
        self.__shader = shader
        self.__shader_2d = shader_2d

        weapon_models_paths = [
            "src/_content/3D_models/bazooka.STL",
            "src/_content/3D_models/machine_gun.STL",
            "src/_content/3D_models/laser_gun.STL",
            "src/_content/3D_models/shotgun.STL"
        ]

        none_positions, block_positions = game_field.return_block_positions()

        if block_positions:
            for num in range(5):
                while True:
                    new_weapon = self.__create_weapon(weapon_models_paths, block_positions, none_positions)

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
            image_paths: list[str],
            block_positions: list[tuple[int, int]],
            none_positions: list[tuple[int, int]]
    ) -> Weapon:

        model_path = random.choice(image_paths)

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

        flip_x = False
        if model_path == "src/_content/3D_models/machine_gun.STL" \
                or model_path == "src/_content/3D_models/shotgun.STL":
            flip_x = True

        weapon_type = WeaponEnum.MACHINE_GUN
        if model_path == "src/_content/3D_models/machine_gun.STL":
            weapon_type = WeaponEnum.MACHINE_GUN
        elif model_path == "src/_content/3D_models/laser_gun.STL":
            weapon_type = WeaponEnum.LASER_GUN
        elif model_path == "src/_content/3D_models/bazooka.STL":
            weapon_type = WeaponEnum.BAZOOKA

        return Weapon(self.__shader, self.__shader_2d, weapon_pos, weapon_type, model_path)

    def draw(self, projection: 'np.ndarray', view: 'np.ndarray', t: float,
             light_pos: 'np.ndarray', camera_pos: 'np.ndarray') -> None:
        for weapon in self:
            weapon.draw(projection, view, t, light_pos, camera_pos)
