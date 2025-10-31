from OpenGL.GL import *  # type: ignore
import numpy


class Block:
    def __init__(self, vertices: list[float]) -> None:

        self.__vertices = numpy.array(vertices, dtype=numpy.float32)
        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)
        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)

        glBufferData(GL_ARRAY_BUFFER, self.__vertices.nbytes, self.__vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self):
        glBindVertexArray(self.__vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
