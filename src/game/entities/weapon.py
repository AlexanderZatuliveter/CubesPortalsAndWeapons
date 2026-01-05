

import numpy as np
from OpenGL.GL import *  # type: ignore

from engine.graphics.opengl_3d_utils import MeshData, OpenGL_3D_Utils
from engine.graphics.renderer import Renderer
from game.enums.weapon_enum import WeaponEnum
from game.systems.float_rect import FloatRect
from game.consts import BLOCK_SIZE


class Weapon:
    def __init__(
        self,
        shader,
        shader_2d,
        position: tuple[float, float],
        type: WeaponEnum,
        model_mesh: MeshData
    ) -> None:

        self.__shader = shader
        self.__type = type
        self.__position = position  # world position (x, y)
        self.__model_mesh = model_mesh

        self.rect = FloatRect(*self.__position, BLOCK_SIZE * 2, BLOCK_SIZE * 1)

        self.__vao = glGenVertexArrays(1)
        vbo_pos = glGenBuffers(1)
        vbo_norm = glGenBuffers(1)
        self.__ebo_faces = glGenBuffers(1)
        self.__ebo_edges = glGenBuffers(1)

        glBindVertexArray(self.__vao)

        # Positions
        glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, model_mesh.vertices.nbytes, model_mesh.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Normals
        glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
        glBufferData(GL_ARRAY_BUFFER, model_mesh.normals.nbytes, model_mesh.normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # Faces EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.__ebo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, model_mesh.faces.nbytes, model_mesh.faces, GL_STATIC_DRAW)

        glBindVertexArray(0)

        # Edges EBO (можно биндать по необходимости)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.__ebo_edges)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, model_mesh.edges.nbytes, model_mesh.edges, GL_STATIC_DRAW)

    def draw(self, projection: 'np.ndarray', view: 'np.ndarray', t: float,
             light_pos: 'np.ndarray', camera_pos: 'np.ndarray') -> None:

        model = OpenGL_3D_Utils.rotate(t)
        translate = OpenGL_3D_Utils.translate(self.__position[0], self.__position[1], 0.0)
        scale_factor = BLOCK_SIZE * 2.0
        scale_mat = OpenGL_3D_Utils.scale(scale_factor, scale_factor, scale_factor)
        # Order: projection @ view @ translate(world) @ scale(local) @ rotate(local)
        mvp = projection @ view @ translate @ scale_mat @ model

        glUniformMatrix4fv(glGetUniformLocation(self.__shader, "mvp"), 1, GL_TRUE, mvp)
        glUniformMatrix4fv(glGetUniformLocation(self.__shader, "model"), 1, GL_TRUE, model)
        glUniform3fv(glGetUniformLocation(self.__shader, "lightPos"), 1, light_pos)
        glUniform3fv(glGetUniformLocation(self.__shader, "viewPos"), 1, camera_pos)

        glBindVertexArray(self.__vao)

        # --- Draw faces (opaque) ---
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        glUniform3f(glGetUniformLocation(self.__shader, "objectColor"), 0.4, 0.4, 0.45)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.__ebo_faces)
        glDrawElements(GL_TRIANGLES, len(self.__model_mesh.faces), GL_UNSIGNED_INT, None)

        glDisable(GL_POLYGON_OFFSET_FILL)
        glEnable(GL_BLEND)

    def get_type(self) -> WeaponEnum:
        return self.__type
