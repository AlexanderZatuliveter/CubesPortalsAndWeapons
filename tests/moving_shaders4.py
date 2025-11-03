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
layout(location = 0) in vec2 aPos;

uniform mat4 uMVP;

void main()
{
    gl_Position = uMVP * vec4(aPos, 0.0, 1.0);
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
# MATRIX HELPERS
# =============================


def ortho(l, r, b, t, n, f):
    return np.array([
        [2 / (r - l), 0, 0, -(r + l) / (r - l)],
        [0, 2 / (t - b), 0, -(t + b) / (t - b)],
        [0, 0, -2 / (f - n), -(f + n) / (f - n)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def translate(tx, ty, tz):
    M = np.identity(4, dtype=np.float32)
    M[3][0] = tx
    M[3][1] = ty
    M[3][2] = tz
    return M


# =============================
# SHADERS CREATION
# =============================

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(glGetShaderInfoLog(shader))
        raise RuntimeError("Shader compile failed")

    return shader


def create_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)

    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)

    if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
        print(glGetProgramInfoLog(prog))
        raise RuntimeError("Link error")

    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog


# =============================
# GEOMETRY HELPERS
# =============================

def create_polygon(n, size):
    """n-угольник в центре (0,0)"""
    arr = []
    for i in range(n):
        a = i * 2 * math.pi / n
        arr.append(math.cos(a) * size)
        arr.append(math.sin(a) * size)
    return np.array(arr, dtype=np.float32)


# =============================
# MAIN
# =============================

def main():
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

    program = create_program(VERT_SRC, FRAG_SRC)
    glUseProgram(program)

    # -------------------------
    # Dynamic objects
    # -------------------------

    # square
    square_vertices = np.array([
        -0.1, -0.1,
        0.1, -0.1,
        0.1, 0.1,
        -0.1, 0.1,
    ], dtype=np.float32)

    square_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, square_vbo)
    glBufferData(GL_ARRAY_BUFFER, square_vertices.nbytes, square_vertices, GL_STATIC_DRAW)

    square_vao = glGenVertexArrays(1)
    glBindVertexArray(square_vao)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    # Hexagon
    hex_vertices = create_polygon(6, 0.1)
    hex_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, hex_vbo)
    glBufferData(GL_ARRAY_BUFFER, hex_vertices.nbytes, hex_vertices, GL_STATIC_DRAW)

    hex_vao = glGenVertexArrays(1)
    glBindVertexArray(hex_vao)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    glBindVertexArray(0)

    # -------------------------
    # Static objects
    # -------------------------

    STATIC_COUNT = 10000
    static_positions = []
    static_forms = []

    for _ in range(STATIC_COUNT):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        static_positions.append((x, y))
        static_forms.append(random.choice(["square", "hex"]))

    # -------------------------

    uMVP = glGetUniformLocation(program, "uMVP")
    uColor = glGetUniformLocation(program, "uColor")

    projection = ortho(-1, 1, -1, 1, -1, 1)

    sq_pos = [0.0, 0.0]
    hex_pos = [0.3, 0.3]

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Square movement (arrows)
        if keys[K_LEFT]:
            sq_pos[0] -= dt
        if keys[K_RIGHT]:
            sq_pos[0] += dt
        if keys[K_UP]:
            sq_pos[1] += dt
        if keys[K_DOWN]:
            sq_pos[1] -= dt

        # Hex movement (WASD)
        if keys[K_a]:
            hex_pos[0] -= dt
        if keys[K_d]:
            hex_pos[0] += dt
        if keys[K_w]:
            hex_pos[1] += dt
        if keys[K_s]:
            hex_pos[1] -= dt

        glClear(GL_COLOR_BUFFER_BIT)

        # Draw static objects
        for (x, y), form in zip(static_positions, static_forms):
            model = translate(x, y, 0)
            mvp = projection @ model
            glUniformMatrix4fv(uMVP, 1, GL_FALSE, mvp)
            glUniform3f(uColor, 0.4, 0.4, 0.4)

            if form == "square":
                glBindVertexArray(square_vao)
                glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
            else:
                glBindVertexArray(hex_vao)
                glDrawArrays(GL_TRIANGLE_FAN, 0, 6)

        # Moving square
        model = translate(sq_pos[0], sq_pos[1], 0)
        mvp = projection @ model
        glUniformMatrix4fv(uMVP, 1, GL_FALSE, mvp)
        glUniform3f(uColor, 0.1, 0.7, 1.0)

        glBindVertexArray(square_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        # Moving hex
        model = translate(hex_pos[0], hex_pos[1], 0)
        mvp = projection @ model
        glUniformMatrix4fv(uMVP, 1, GL_FALSE, mvp)
        glUniform3f(uColor, 1.0, 0.7, 0.1)

        glBindVertexArray(hex_vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 6)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
