
import random
from OpenGL.GL.shaders import ShaderProgram

from game.consts import BLOCK_SIZE
from game.entities.weapon import Weapon
from game.game_field import GameField


class Weapons:
    def __init__(self, game_field: GameField, shader: ShaderProgram | None) -> None:
        self.__shader = shader

        weapon_image_paths = [
            "src/_content/images/bazooka.png",
            "src/_content/images/machine_gun.png",
            "src/_content/images/laser_gun.png",
            "src/_content/images/shotgun.png"
        ]

        none_positions, block_positions = game_field.return_block_positions()

        self.__weapons: list[Weapon] = []
        if block_positions:
            for num in range(5):
                while True:
                    new_weapon = self.__create_weapon(weapon_image_paths, block_positions, none_positions)

                    invalid = False
                    for weapon in self.__weapons:
                        if new_weapon.rect.colliderect(weapon.rect):
                            invalid = True
                            break

                    if invalid:
                        continue

                    self.__weapons.append(new_weapon)
                    break

    def __create_weapon(
            self,
            image_paths: list[str],
            block_positions: list[tuple[int, int]],
            none_positions: list[tuple[int, int]]
    ) -> Weapon:

        image_path = random.choice(image_paths)

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
        if image_path == "src/_content/images/machine_gun.png" \
                or image_path == "src/_content/images/shotgun.png":
            flip_x = True

        return Weapon(self.__shader, image_path, weapon_pos, flip_x=flip_x)

    def draw(self) -> None:
        for weapon in self.__weapons:
            weapon.draw()
