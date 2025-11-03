import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np
import ctypes

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
out vec4 FragColor;
uniform vec3 uColor;

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
    M[3][0], M[3][1], M[3][2] = tx, ty, tz
    return M

# =============================
# SHADER COMPILATION
# =============================


def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(glGetShaderInfoLog(shader))
        raise RuntimeError("Shader compile error")

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
        raise RuntimeError("Shader link error")

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

    # --------
    # OBJECT 1 — SQUARE
    # --------
    square = np.array([
        -0.1, -0.1,
        0.1, -0.1,
        0.1, 0.1,
        -0.1, 0.1,
    ], dtype=np.float32)

    # --------
    # OBJECT 2 — HEXAGON (6-sided)
    # --------
    hex_coords = []
    R = 0.12
    for i in range(6):
        angle = i * (2 * np.pi / 6)
        x = np.cos(angle) * R
        y = np.sin(angle) * R
        hex_coords.append(x)
        hex_coords.append(y)

    hexagon = np.array(hex_coords, dtype=np.float32)

    # Create VBOs
    VBOs = glGenBuffers(2)
    VBO_square, VBO_hex = VBOs

    # Upload square
    glBindBuffer(GL_ARRAY_BUFFER, VBO_square)
    glBufferData(GL_ARRAY_BUFFER, square.nbytes, square, GL_STATIC_DRAW)

    # Upload hexagon
    glBindBuffer(GL_ARRAY_BUFFER, VBO_hex)
    glBufferData(GL_ARRAY_BUFFER, hexagon.nbytes, hexagon, GL_STATIC_DRAW)

    # VAO
    VAOs = glGenVertexArrays(2)
    VAO_square, VAO_hex = VAOs

    # Square VAO
    glBindVertexArray(VAO_square)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_square)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))

    # Hexagon VAO
    glBindVertexArray(VAO_hex)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_hex)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, ctypes.c_void_p(0))

    glBindVertexArray(0)

    # Uniforms
    uMVP_loc = glGetUniformLocation(program, "uMVP")
    uColor_loc = glGetUniformLocation(program, "uColor")

    # Static projection
    projection = ortho(-1, 1, -1, 1, -1, 1)

    # Positions
    p1x, p1y = -0.3, 0.0   # square
    p2x, p2y = 0.3, 0.0   # hexagon

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        speed = 0.7

        # Square — arrows
        if keys[K_LEFT]:
            p1x -= speed * dt
        if keys[K_RIGHT]:
            p1x += speed * dt
        if keys[K_UP]:
            p1y += speed * dt
        if keys[K_DOWN]:
            p1y -= speed * dt

        # Hexagon — WASD
        if keys[K_a]:
            p2x -= speed * dt
        if keys[K_d]:
            p2x += speed * dt
        if keys[K_w]:
            p2y += speed * dt
        if keys[K_s]:
            p2y -= speed * dt

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program)

        # =============
        # Draw square
        # =============
        model1 = translate(p1x, p1y, 0.0)
        mvp1 = projection @ model1
        glUniformMatrix4fv(uMVP_loc, 1, GL_FALSE, mvp1)
        glUniform3f(uColor_loc, 0.1, 0.7, 1.0)

        glBindVertexArray(VAO_square)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        # =============
        # Draw hexagon
        # =============
        model2 = translate(p2x, p2y, 0.0)
        mvp2 = projection @ model2
        glUniformMatrix4fv(uMVP_loc, 1, GL_FALSE, mvp2)
        glUniform3f(uColor_loc, 1.0, 0.4, 0.2)

        glBindVertexArray(VAO_hex)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 6)

        glBindVertexArray(0)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
