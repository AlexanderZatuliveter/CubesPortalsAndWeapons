from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
from numpy import ndarray
import ctypes

from consts import BLOCK_SIZE, DARK_GREY


class Block:
    def __init__(self, shader: ShaderProgram) -> None:
        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(shader, "uColor")
        self.__offset_x = 0.0
        self.__offset_y = 0.0

        # Create square vertices
        vertices = np.array([
            # Position (x, y)
            0.0, 0.0,                    # Bottom-left
            BLOCK_SIZE, 0.0,             # Bottom-right
            BLOCK_SIZE, BLOCK_SIZE,      # Top-right
            0.0, BLOCK_SIZE,             # Top-left
        ], dtype=np.float32)

        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        # Create and bind vertex buffer
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        # Create and bind offset buffer
        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        # Offset attribute
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
        glBindVertexArray(self.__vao)
        glUniform1i(self.__uIsPlayer, 0)
        glUniform3f(self.__uColor, *DARK_GREY)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)
        glBindVertexArray(0)
