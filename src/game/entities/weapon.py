

import numpy as np
from OpenGL.GL.shaders import ShaderProgram
from OpenGL.GL import *  # type: ignore

from engine.graphics.opengl_3d_utils import MeshData
from engine.graphics.renderer_3d import Renderer3D
from game.enums.weapon_enum import WeaponEnum
from game.systems.float_rect import FloatRect
from game.consts import BLOCK_SIZE


class Weapon:
    def __init__(
        self,
        shader: ShaderProgram | None,
        position: tuple[float, float],
        type: WeaponEnum,
        model_mesh: MeshData
    ) -> None:

        self.__shader = shader
        self.__type = type
        self.__position = position  # world position (x, y)
        self.__model_mesh = model_mesh

        self.__width = BLOCK_SIZE * 2
        self.__height = BLOCK_SIZE * 1
        self.__depth = BLOCK_SIZE * 2

        self.rect = FloatRect(
            self.__position[0] - self.__width / 2,
            self.__position[1] - self.__height / 2,
            self.__width,
            self.__height
        )

        self.__renderer = Renderer3D()
        self.__vao, self.__ebo_faces, self.__ebo_edges = self.__renderer.create_vao_ebo(self.__model_mesh)

    def draw(
        self,
        projection: 'np.ndarray',
        view: 'np.ndarray',
        t: float,
        light_pos: 'np.ndarray',
        camera_pos: 'np.ndarray'
    ) -> None:

        self.__renderer.draw_3d_model(
            position=self.__position,
            size=(self.__width, self.__height, self.__depth),
            color=(0.4, 0.4, 0.45),
            vao=self.__vao,
            ebo_faces=self.__ebo_faces,
            shader=self.__shader,
            model_mesh=self.__model_mesh,
            projection=projection,
            view=view,
            t=t,
            light_pos=light_pos,
            camera_pos=camera_pos
        )

    def change_position(self, position: tuple[float, float]) -> None:
        self.__position = position
        self.rect = FloatRect(*self.__position, BLOCK_SIZE * 2, BLOCK_SIZE * 1)

    def get_type(self) -> WeaponEnum:
        return self.__type
