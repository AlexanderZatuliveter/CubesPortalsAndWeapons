import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import ctypes
import random


# =============================
# SHADERS
# =============================

VERT_SRC = """
#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aOffset; // только для инстансов

uniform mat4 uProjection;
uniform vec2 uPlayerPos;
uniform int uIsPlayer;

void main()
{
    vec2 pos = aPos;
    if(uIsPlayer == 0)
        pos += aOffset;   // враги инстансинг
    else
        pos += uPlayerPos; // игрок

    gl_Position = uProjection * vec4(pos, 0.0, 1.0);
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

# Ортографическая проекция с top-left origin
# (0,0) — верхний левый угол
# Y растёт вниз
def ortho(l, r, b, t, n, f):
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (b - t), 0, -(b + t) / (b - t)],
        [0, 0, -2 / (f - n), -(f + n) / (f - n)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


# =============================
# SHADER UTILS
# =============================

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        log = glGetShaderInfoLog(shader).decode('utf-8')
        raise RuntimeError(f"Shader compile error:\n{log}")
    return shader


def create_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
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


# =============================
# MAIN
# =============================

def main():
    WIDTH, HEIGHT = 800, 600
    pygame.init()

    # Требуем OpenGL 3.3 Core
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)

    glViewport(0, 0, WIDTH, HEIGHT)
    glClearColor(0, 0, 0, 1)

    program = create_program(VERT_SRC, FRAG_SRC)
    glUseProgram(program)

    # Квадрат 30×30
    size = 30
    square = np.array([
        [0, 0],
        [size, 0],
        [size, size],
        [0, size],
    ], dtype=np.float32)

    # ========== VBO — квадрат ==========
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, square.nbytes, square, GL_STATIC_DRAW)

    # =========================================
    # OBJECT INSTANCING
    # =========================================
    NUM = 100
    positions = np.random.uniform(
        low=[0, 0],
        high=[WIDTH - size, HEIGHT - size],
        size=(NUM, 2)
    ).astype(np.float32)

    vbo_offsets = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_offsets)
    glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

    # VAO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    stride = 2 * 4  # sizeof(vec2)

    # vertices
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # offsets
    glBindBuffer(GL_ARRAY_BUFFER, vbo_offsets)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribDivisor(1, 1)

    glBindVertexArray(0)

    # Uniforms
    uProjection = glGetUniformLocation(program, "uProjection")
    uPlayerPos = glGetUniformLocation(program, "uPlayerPos")
    uColor = glGetUniformLocation(program, "uColor")
    uIsPlayer = glGetUniformLocation(program, "uIsPlayer")

    # === Top-left ortho ===
    projection = ortho(0, WIDTH, 0, HEIGHT, -1, 1)
    glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection.T)

    # Player pos (center initially)
    x, y = WIDTH // 2, HEIGHT // 2

    clock = pygame.time.Clock()
    running = True

    speed = 300

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            x -= speed * dt
        if keys[K_RIGHT]:
            x += speed * dt
        if keys[K_UP]:
            y -= speed * dt   # y вниз
        if keys[K_DOWN]:
            y += speed * dt   # y вверх

        # clamp
        x = max(0, min(x, WIDTH - size))
        y = max(0, min(y, HEIGHT - size))

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program)
        glBindVertexArray(VAO)

        # === Draw INSTANCED OBJECTS ===
        glUniform1i(uIsPlayer, 0)
        glUniform3f(uColor, 0.5, 0.5, 0.5)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 4, NUM)

        # === Draw PLAYER ===
        glUniform1i(uIsPlayer, 1)
        glUniform2f(uPlayerPos, x, y)
        glUniform3f(uColor, 0.1, 0.7, 1.0)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
