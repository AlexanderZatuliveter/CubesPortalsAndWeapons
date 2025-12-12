

from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from consts import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH


def ortho(l, r, b, t, n, f):
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (b - t), 0, -(b + t) / (b - t)],
        [0, 0, -2 / (f - n), -(f + n) / (f - n)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


def set_screen_size(screen: pygame.Surface, shader: ShaderProgram | None,
                    screen_size: tuple[int, int]) -> pygame.Surface:
    # Set up the viewport to maintain aspect ratio
    screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
    glViewport(0, 0, *screen_size)

    # Update the projection matrix in the shader
    glUseProgram(shader)
    uProjection = glGetUniformLocation(shader, "uProjection")
    projection = ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
    glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection.T)

    return screen


def resize_display(
    screen: pygame.Surface,
    shader: ShaderProgram | None,
    past_screen_size: tuple[float, float],
    new_screen_size: tuple[int, int]
) -> tuple[pygame.Surface, tuple[float, float]] | None:
    """Handle window resizing while maintaining the aspect ratio."""

    if past_screen_size == new_screen_size:
        return

    ratio_w = new_screen_size[0] / GAME_FIELD_WIDTH
    ratio_h = new_screen_size[1] / GAME_FIELD_HEIGHT

    if past_screen_size[0] != new_screen_size[0] and past_screen_size[1] != new_screen_size[1]:
        ratio = min(ratio_w, ratio_h)
    elif past_screen_size[0] != new_screen_size[0]:
        ratio = ratio_w
    elif past_screen_size[1] != new_screen_size[1]:
        ratio = ratio_h

    new_width = int(GAME_FIELD_WIDTH * ratio)
    new_height = int(GAME_FIELD_HEIGHT * ratio)

    screen = set_screen_size(screen, shader, (new_width, new_height))
    past_screen_size = pygame.display.get_window_size()

    return screen, past_screen_size


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


def create_shader(vertex_filepath, fragment_filepath):
    vs = compile_shader(vertex_filepath, GL_VERTEX_SHADER)
    fs = compile_shader(fragment_filepath, GL_FRAGMENT_SHADER)
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
