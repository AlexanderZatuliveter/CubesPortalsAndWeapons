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

void main()
{
    FragColor = vec4(0.1, 0.7, 1.0, 1.0);
}
"""

# =============================
# MATRIX HELPERS
# =============================


def ortho(l, r, b, t, n, f):
    """Orthographic projection matrix"""
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

    # Create shader program
    program = create_program(VERT_SRC, FRAG_SRC)
    glUseProgram(program)

    # Vertex data for square (centered at origin)
    # Only VBO, VAO — optimal. No frequent updates.
    vertices = np.array([
        -0.1, -0.1,
        0.1, -0.1,
        0.1, 0.1,
        -0.1, 0.1,
    ], dtype=np.float32)

    # Single VBO
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # VAO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(
        0, 2, GL_FLOAT, GL_FALSE,
        2 * 4, ctypes.c_void_p(0)
    )

    # No element buffer → draw with triangle fan
    # (for a simple square this is fine; can use EBO too)

    glBindVertexArray(0)

    # Uniform
    uMVP_loc = glGetUniformLocation(program, "uMVP")

    # Projection (static, camera doesn’t move)
    projection = ortho(-1, 1, -1, 1, -1, 1)

    # Player position
    px, py = 0.0, 0.0

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movement
        keys = pygame.key.get_pressed()
        speed = 0.7

        if keys[pygame.K_LEFT]:
            px -= speed * dt
        if keys[pygame.K_RIGHT]:
            px += speed * dt
        if keys[pygame.K_UP]:
            py += speed * dt
        if keys[pygame.K_DOWN]:
            py -= speed * dt

        # Compute matrices
        model = translate(px, py, 0.0)

        # MVP
        mvp = projection @ model  # (View = identity)

        # Render
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(program)
        glUniformMatrix4fv(uMVP_loc, 1, GL_FALSE, mvp)

        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
