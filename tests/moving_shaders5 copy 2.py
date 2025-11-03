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

def ortho(l, r, b, t, n, f):
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (t - b), 0, -(t + b) / (t - b)],
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
    WIDTH, HEIGHT = 800, 600
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)

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

    # VBO — квадрат
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, square.nbytes, square, GL_STATIC_DRAW)

    # =========================================
    # OBJECT INSTANCING
    # =========================================
    NUM = 100
    positions = []

    for _ in range(NUM):
        positions.append([
            random.uniform(0, WIDTH - size),
            random.uniform(0, HEIGHT - size)
        ])

    positions = np.array(positions, dtype=np.float32)

    vbo_offsets = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_offsets)
    glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)

    # VAO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    stride = 2 * 4

    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

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

    projection = ortho(0, WIDTH, 0, HEIGHT, -1, 1)

    glUniformMatrix4fv(uProjection, 1, GL_TRUE, projection)

    # Player pos
    x, y = WIDTH // 2, HEIGHT // 2

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        keys = pygame.key.get_pressed()
        speed = 300

        if keys[K_LEFT]:
            x -= speed * dt
        if keys[K_RIGHT]:
            x += speed * dt
        if keys[K_UP]:
            y += speed * dt
        if keys[K_DOWN]:
            y -= speed * dt

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
