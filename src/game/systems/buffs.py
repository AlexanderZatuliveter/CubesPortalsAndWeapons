
import random
from OpenGL.GL.shaders import ShaderProgram
import numpy as np

from engine.graphics.opengl_3d_utils import OpenGL_3D_Utils
from game.consts import BLOCK_SIZE
from game.entities.buff import Buff
from game.enums.buff_enum import BuffEnum
from game.game_field import GameField


class Buffs(list[Buff]):
    def __init__(self, game_field: GameField, shader: ShaderProgram | None) -> None:
        self.__shader = shader

        self.__buffs = {
            BuffEnum.ENDLESS_HEALTH: OpenGL_3D_Utils.load("src/_content/3D_models/buffs/heart.STL"),
            BuffEnum.STRENGTH_INCREASE: OpenGL_3D_Utils.load("src/_content/3D_models/buffs/energy_drink.STL")
        }

        none_positions, block_positions = game_field.return_block_positions()

        if block_positions:
            for num in range(3):
                while True:
                    new_buff = self.__create_buff(
                        block_positions,
                        none_positions
                    )

                    invalid = False

                    for buff in self:
                        if new_buff.rect.colliderect(buff.rect):
                            invalid = True
                            break

                    if invalid:
                        continue

                    self.append(new_buff)
                    break

    def __create_buff(
        self,
        block_positions: list[tuple[int, int]],
        none_positions: list[tuple[int, int]]
    ) -> Buff:

        model = random.choice(list(self.__buffs.keys()))

        while True:
            buff_pos = random.choice(none_positions)

            if (buff_pos[0], buff_pos[1] + BLOCK_SIZE) not in block_positions:
                continue
            if (buff_pos[0], buff_pos[1] - BLOCK_SIZE) in block_positions \
                    or (buff_pos[0] + BLOCK_SIZE, buff_pos[1] - BLOCK_SIZE) in block_positions:
                continue
            if (buff_pos[0] + BLOCK_SIZE, buff_pos[1]) in block_positions:
                continue

            break

        return Buff(self.__shader, buff_pos, model, self.__buffs[model])

    def draw(self, projection: 'np.ndarray', view: 'np.ndarray', t: float,
             light_pos: 'np.ndarray', camera_pos: 'np.ndarray') -> None:
        for buff in self:
            buff.draw(projection, view, t, light_pos, camera_pos)
