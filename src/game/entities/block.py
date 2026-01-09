
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import ctypes

from game.consts import BLOCK_SIZE, DARK_GREY
from game.systems.float_rect import FloatRect
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.renderer import Renderer


class Block:
    def __init__(self, shader: ShaderProgram) -> None:
        self.rect = FloatRect(0.0, 0.0, BLOCK_SIZE, BLOCK_SIZE)

        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uColor = glGetUniformLocation(shader, "uColor")

        self.__offset_x = 0.0
        self.__offset_y = 0.0

        self.__renderer = Renderer()

        vertices = OpenGLUtils.create_square_vertices(BLOCK_SIZE)
        self.__vertex_count = 4
        self.__vao, self.__vbo = self.__renderer.create_vao_vbo(vertices)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # This makes it an instance attribute

    def set_offset(self, x: float, y: float) -> None:
        self.__offset_x = x
        self.__offset_y = y

        # Update offset buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([x, y], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

    def draw(self) -> None:
        self.__renderer.draw_rect(
            self.__vao, (self.__uUseTexture, False),
            (self.__uIsPlayer, False), None,
            self.__uColor, self.rect, DARK_GREY,
            self.__vertex_count
        )
