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
layout(location = 0) in vec2 aPos;     // локальные вершины (в пикселях)
layout(location = 1) in vec2 aOffset;  // смещение экземпляра / смещение динамического объекта

uniform mat4 uProjection;

void main()
{
    vec2 worldPos = aPos + aOffset;               // позиция в мировых координатах (пиксели)
    gl_Position = uProjection * vec4(worldPos, 0.0, 1.0);
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

# =============================
# SHADER COMPILATION
# =============================


def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader


def create_program(vs_src, fs_src):
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(prog).decode())
    glDeleteShader(vs)
    glDeleteShader(fs)
    return prog

# =============================
# HELP: polygon
# =============================


def create_regular_polygon(n, radius):
    coords = []
    for i in range(n):
        a = i * (2.0 * math.pi / n)
        coords.append(math.cos(a) * radius)
        coords.append(math.sin(a) * radius)
    return np.array(coords, dtype=np.float32)

# =============================
# MAIN
# =============================


def main():
    pygame.init()
    screen_w, screen_h = 800, 600
    pygame.display.set_mode((screen_w, screen_h), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Instancing: static + 2 moving objects")

    program = create_program(VERT_SRC, FRAG_SRC)
    glUseProgram(program)

    # projection (в пикселях)
    projection = ortho(0, screen_w, 0, screen_h, -1.0, 1.0)
    uProjection_loc = glGetUniformLocation(program, "uProjection")
    uColor_loc = glGetUniformLocation(program, "uColor")
    glUniformMatrix4fv(uProjection_loc, 1, GL_FALSE, projection)

    # ========== SHAPES (локальные вершины в пикселях) ==========
    # Square centered at (0,0), size = 40x40 -> half = 20
    half_sq = 20.0
    square_vertices = np.array([
        -half_sq, -half_sq,
        half_sq, -half_sq,
        half_sq, half_sq,
        -half_sq, half_sq,
    ], dtype=np.float32)

    # Hexagon centered at (0,0), radius = 18
    hex_vertices = create_regular_polygon(6, 18.0)

    # ========== STATIC INSTANCED POSITIONS ==========
    NUM_STATIC_SQUARES = 600
    NUM_STATIC_HEX = 400

    static_square_pos = np.array([
        (random.uniform(0 + half_sq, screen_w - half_sq),
         random.uniform(0 + half_sq, screen_h - half_sq))
        for _ in range(NUM_STATIC_SQUARES)
    ], dtype=np.float32)

    static_hex_pos = np.array([
        (random.uniform(0 + 18.0, screen_w - 18.0),
         random.uniform(0 + 18.0, screen_h - 18.0))
        for _ in range(NUM_STATIC_HEX)
    ], dtype=np.float32)

    # ========== VBOs & VAOs ==========
    # Square vertex VBO
    vbo_sq_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_sq_vertices)
    glBufferData(GL_ARRAY_BUFFER, square_vertices.nbytes, square_vertices, GL_STATIC_DRAW)

    # Hex vertex VBO
    vbo_hex_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_hex_vertices)
    glBufferData(GL_ARRAY_BUFFER, hex_vertices.nbytes, hex_vertices, GL_STATIC_DRAW)

    # Instance offset VBOs for static objects
    vbo_static_sq_offsets = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_static_sq_offsets)
    glBufferData(GL_ARRAY_BUFFER, static_square_pos.nbytes, static_square_pos, GL_STATIC_DRAW)

    vbo_static_hex_offsets = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_static_hex_offsets)
    glBufferData(GL_ARRAY_BUFFER, static_hex_pos.nbytes, static_hex_pos, GL_STATIC_DRAW)

    # Dynamic offset buffers (single vec2, we will update per-frame)
    vbo_dyn_sq_offset = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_sq_offset)
    glBufferData(GL_ARRAY_BUFFER, 2 * 4, None, GL_DYNAMIC_DRAW)  # 2 floats

    vbo_dyn_hex_offset = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_hex_offset)
    glBufferData(GL_ARRAY_BUFFER, 2 * 4, None, GL_DYNAMIC_DRAW)

    # --- VAO for instanced squares (static) ---
    vao_inst_sq = glGenVertexArrays(1)
    glBindVertexArray(vao_inst_sq)
    # attribute 0 -> vertex positions
    glBindBuffer(GL_ARRAY_BUFFER, vbo_sq_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # attribute 1 -> instance offsets
    glBindBuffer(GL_ARRAY_BUFFER, vbo_static_sq_offsets)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribDivisor(1, 1)  # one offset per instance
    glBindVertexArray(0)

    # --- VAO for instanced hexes (static) ---
    vao_inst_hex = glGenVertexArrays(1)
    glBindVertexArray(vao_inst_hex)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_hex_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_static_hex_offsets)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribDivisor(1, 1)
    glBindVertexArray(0)

    # --- VAO for dynamic square (uses dynamic offset buffer, divisor = 0) ---
    vao_dyn_sq = glGenVertexArrays(1)
    glBindVertexArray(vao_dyn_sq)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_sq_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # attribute 1 will read from dynamic offset buffer (single vec2)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_sq_offset)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribDivisor(1, 0)  # same value for all vertices -> acts as model translation
    glBindVertexArray(0)

    # --- VAO for dynamic hex ---
    vao_dyn_hex = glGenVertexArrays(1)
    glBindVertexArray(vao_dyn_hex)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_hex_vertices)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_hex_offset)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribDivisor(1, 0)
    glBindVertexArray(0)

    # ========== initial positions for dynamic objects ==========
    player_sq = np.array([100.0, 100.0], dtype=np.float32)   # square (arrows)
    player_hex = np.array([300.0, 200.0], dtype=np.float32)  # hexagon (WASD)

    # Clear color
    glClearColor(0.08, 0.08, 0.08, 1.0)

    clock = pygame.time.Clock()
    running = True

    # speed in pixels per second
    speed = 200.0

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        keys = pygame.key.get_pressed()
        # square: arrows
        if keys[K_LEFT]:
            player_sq[0] -= speed * dt
        if keys[K_RIGHT]:
            player_sq[0] += speed * dt
        if keys[K_UP]:
            player_sq[1] += speed * dt
        if keys[K_DOWN]:
            player_sq[1] -= speed * dt

        # hex: WASD
        if keys[K_a]:
            player_hex[0] -= speed * dt
        if keys[K_d]:
            player_hex[0] += speed * dt
        if keys[K_w]:
            player_hex[1] += speed * dt
        if keys[K_s]:
            player_hex[1] -= speed * dt

        # clamp into screen (simple)
        player_sq[0] = np.clip(player_sq[0], half_sq, screen_w - half_sq)
        player_sq[1] = np.clip(player_sq[1], half_sq, screen_h - half_sq)
        player_hex[0] = np.clip(player_hex[0], 18.0, screen_w - 18.0)
        player_hex[1] = np.clip(player_hex[1], 18.0, screen_h - 18.0)

        # update dynamic offset buffers (small upload)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_sq_offset)
        glBufferSubData(GL_ARRAY_BUFFER, 0, player_sq.tobytes())

        glBindBuffer(GL_ARRAY_BUFFER, vbo_dyn_hex_offset)
        glBufferSubData(GL_ARRAY_BUFFER, 0, player_hex.tobytes())

        # ========== RENDER ==========
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(program)
        # projection is constant; but set every frame is fine
        glUniformMatrix4fv(uProjection_loc, 1, GL_FALSE, projection)

        # --- Draw static squares (instanced) ---
        glUniform3f(uColor_loc, 0.45, 0.45, 0.45)
        glBindVertexArray(vao_inst_sq)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 4, NUM_STATIC_SQUARES)

        # --- Draw static hexes (instanced) ---
        glUniform3f(uColor_loc, 0.35, 0.55, 0.35)
        glBindVertexArray(vao_inst_hex)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, 6, NUM_STATIC_HEX)

        # --- Draw dynamic square ---
        glUniform3f(uColor_loc, 0.1, 0.7, 1.0)
        glBindVertexArray(vao_dyn_sq)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        # --- Draw dynamic hex ---
        glUniform3f(uColor_loc, 1.0, 0.65, 0.15)
        glBindVertexArray(vao_dyn_hex)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 6)

        glBindVertexArray(0)
        pygame.display.flip()

    # cleanup
    pygame.quit()


if __name__ == "__main__":
    main()
