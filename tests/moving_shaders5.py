import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import ctypes
import random
import math

# =============================
# SHADERS
# =============================

VERT_SRC = """
#version 330 core

layout (location = 0) in vec2 aPos;        // локальные вершины квадрата
layout (location = 1) in vec2 aOffset;     // позиция экземпляра

uniform mat4 uProjection;

void main()
{
    vec2 p = aPos + aOffset;
    gl_Position = uProjection * vec4(p, 0.0, 1.0);
}
"""

FRAG_SRC = """
#version 330 core

uniform vec3 uColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(uColor, 1.0);
}
"""

# =============================
# MATRIX
# =============================


def ortho(l, r, b, t, n, f):
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (t - b), 0, -(t + b) / (t - b)],
        [0, 0, -2 / (f - n), -(f + n) / (f - n)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


# =============================
# SHADER UTILS
# =============================

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader


def create_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()

    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)

    if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(prog))

    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog


# =============================
# MAIN
# =============================

def main():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

    program = create_program(VERT_SRC, FRAG_SRC)
    glUseProgram(program)

    # =========================================
    # SHAPE GEOMETRY (square, TRIANGLE_FAN)
    # =========================================
    square = np.array([
        [-0.05, -0.05],
        [0.05, -0.05],
        [0.05, 0.05],
        [-0.05, 0.05],
    ], dtype=np.float32)

    # Flatten
    square = square.flatten()

    # VBO for square vertices
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, square.nbytes, square, GL_STATIC_DRAW)

    # =========================================
    # INSTANCE POSITIONS
    # =========================================
    NUM = 1000000
    positions = []

    for _ in range(NUM):
        x = random.uniform(-0.9, 0.9)
        y = random.uniform(-0.9, 0.9)
        positions.append((x, y))

    positions = np.array(positions, dtype=np.float32)

    vbo_offsets = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_offsets)
    glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

    # =========================================
    # VAO setup
    # =========================================
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    stride = 2 * 4   # vec2 = 8 bytes

    # --- attribute 0: vertex local geometry
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # --- attribute 1: instance offset
    glBindBuffer(GL_ARRAY_BUFFER, vbo_offsets)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)

    # divisor = 1 → обновлять раз на экземпляр
    glVertexAttribDivisor(1, 1)

    glBindVertexArray(0)

    uProjection = glGetUniformLocation(program, "uProjection")
    uColor = glGetUniformLocation(program, "uColor")

    projection = ortho(-1, 1, -1, 1, -1, 1)

    # =========================================
    # MOVING OBJECT
    # =========================================
    player = [0.0, 0.0]

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            player[0] -= dt
        if keys[K_RIGHT]:
            player[0] += dt
        if keys[K_UP]:
            player[1] += dt
        if keys[K_DOWN]:
            player[1] -= dt

        glClear(GL_COLOR_BUFFER_BIT)

        # =============================
        # DRAW STATIC INSTANCED SQUARES
        # =============================
        glUseProgram(program)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection)
        glUniform3f(uColor, 0.4, 0.4, 0.4)

        glBindVertexArray(VAO)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 4, NUM)

        # =============================
        # Draw player square
        # (just translated in shader manually)
        # =============================
        # Hack: to draw player, just modify projection into translation
        proj2 = projection.copy()
        proj2[3, 0] += player[0]
        proj2[3, 1] += player[1]

        glUniformMatrix4fv(uProjection, 1, GL_FALSE, proj2)
        glUniform3f(uColor, 0.1, 0.7, 1.0)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
