import numpy
from OpenGL.GL import *

from common import ortho  # type: ignore


class Borders:
    def __init__(
        self
    ) -> None:

        # vertices = [
        #     -0.9, -0.9, 0.0, 1.0, 0.0, 0.0,
        #     0.9, -0.9, 0.0, 1.0, 0.0, 0.0,
        #     0.9, 0.9, 0.0, 1.0, 0.0, 0.0,
        #     -0.9, 0.9, 0.0, 1.0, 0.0, 0.0
        # ]

        # vertices_arr = numpy.array(vertices, dtype=numpy.float32)
        vertices_arr = ortho(-1, 1, -1, 1, -1, 1)
        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)

        glBufferData(GL_ARRAY_BUFFER, vertices_arr.nbytes, vertices_arr, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self):
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
