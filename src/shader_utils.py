
from OpenGL.GL import *  # type: ignore


class ShaderUtils:

    @staticmethod
    def compile_shader(filepath, shader_type):
        with open(filepath, 'r') as f:
            src = f.read()
        shader = glCreateShader(shader_type)
        glShaderSource(shader, src)
        glCompileShader(shader)
        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            log = glGetShaderInfoLog(shader).decode('utf-8')
            raise RuntimeError(f"Shader compile error:\n{log}")
        return shader

    @staticmethod
    def create_shader(vertex_filepath, fragment_filepath):
        vs = ShaderUtils.compile_shader(vertex_filepath, GL_VERTEX_SHADER)
        fs = ShaderUtils.compile_shader(fragment_filepath, GL_FRAGMENT_SHADER)
        prog = glCreateProgram()
        glAttachShader(prog, vs)
        glAttachShader(prog, fs)
        glLinkProgram(prog)
        if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
            log = glGetProgramInfoLog(prog).decode('utf-8')
            raise RuntimeError(f"Program link error:\n{log}")
        glDeleteShader(vs)
        glDeleteShader(fs)
        return prog
