from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import compileProgram, compileShader


class Renderer:

    def __init__(self):
        self.__shader = self.__create_shader("./src/shaders/vertex.vert", "./src/shaders/fragment.frag")

    def __create_shader(self, vertex_filepath: str, fragment_filepath: str):

        with open(vertex_filepath, 'r') as f:
            vertex_src = f.read()

        with open(fragment_filepath, 'r') as f:
            fragment_src = f.read()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader

    def use_shader(self):
        glUseProgram(self.__shader)
