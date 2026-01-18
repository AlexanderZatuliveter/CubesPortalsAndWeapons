
from OpenGL.GLU import *  # type: ignore
from OpenGL.GL import *  # type: ignore
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
import pygame
import ctypes
from mouse_buttons import Mouse
from game.consts import GAME_BG_COLOR, BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_PROPORTIONS, GAME_FIELD_WIDTH, MAP_HEIGHT, MAP_WIDTH, MAPS_CELLS_COLOR, VIRTUAL_BLOCK_COLOR
from engine.shader_utils import ShaderUtils
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.display_manager import DisplayManager
from game.game_field import GameField
from engine.graphics.renderer_2d import Renderer2D
from game.systems.float_rect import FloatRect
import sys
import os

# --- ФИКС ИМПОРТОВ ---
# Добавляем путь к src в sys.path, чтобы видеть модуль game
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


pygame.init()

info = pygame.display.Info()
target_width = int(info.current_w * 0.8)
target_height = int(target_width / GAME_FIELD_PROPORTIONS)
screen_size = (target_width, target_height)

# Создаём окно с поддержкой OpenGL
screen: pygame.Surface = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)

past_screen_size = screen.get_size()

# Enable alpha blending by default for UI and textures
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

shader = ShaderUtils.create_shader("./src/game/_shaders/2d_shader.vert", "./src/game/_shaders/2d_shader.frag")
glUseProgram(shader)

uProjection = glGetUniformLocation(shader, "uProjection")
projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection.T)

# Cache other uniform locations for reuse
uPlayerPos = glGetUniformLocation(shader, "uPlayerPos")
uIsPlayerLoc = glGetUniformLocation(shader, "uIsPlayer")
uUseTextureLoc = glGetUniformLocation(shader, "uUseTexture")
uColorLoc = glGetUniformLocation(shader, "uColor")

mouse = Mouse()
game_field = GameField(
    int(GAME_FIELD_WIDTH // BLOCK_SIZE),
    int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
    shader
)

renderer = Renderer2D()

lines: dict[FloatRect, tuple[int, int]] = {}

thickness = 2

for x in range(1, MAP_WIDTH):
    x = x * BLOCK_SIZE
    vertices = OpenGLUtils.create_rectangle_vertices(
        width=thickness,
        height=GAME_FIELD_HEIGHT,
        x=x - thickness / 2,
        y=0
    )
    vao, vbo = renderer.create_vao_vbo(vertices)
    # Configure vertex attribute for position (location 0)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
    rect = FloatRect(x, 0, width=5, height=GAME_FIELD_HEIGHT)
    lines[rect] = (vao, vbo)

for y in range(1, MAP_HEIGHT):
    y = y * BLOCK_SIZE
    vertices = OpenGLUtils.create_rectangle_vertices(
        width=GAME_FIELD_WIDTH,
        height=thickness,
        x=0,
        y=y - thickness / 2
    )
    vao, vbo = renderer.create_vao_vbo(vertices)
    # Configure vertex attribute for position (location 0)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
    rect = FloatRect(0, y, width=GAME_FIELD_WIDTH, height=5)
    lines[rect] = (vao, vbo)

clock = pygame.time.Clock()

display_manager = DisplayManager()

screen = display_manager.set_screen_size(screen, shader, screen.get_size())

# Set background's color
glClearColor(*GAME_BG_COLOR)


while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if keys[pygame.K_ESCAPE] or event.type == pygame.QUIT:
            print(f"blocks:{mouse.blocks}")
            pygame.quit()
            sys.exit()

        if keys[pygame.K_s]:
            print('saved')
            game_field.save_to_file("pillars.map")

        if keys[pygame.K_l]:
            print('loaded')
            game_field.load_from_file("pillars.map")

        if keys[pygame.K_c]:
            print('cleared')
            game_field.field.fill(None)

        if event.type == pygame.VIDEORESIZE:
            videoresize = display_manager.resize_display(screen, shader, past_screen_size, event.size)

            if videoresize is not None:
                screen, past_screen_size = videoresize

    mouse.update(game_field, screen)

    # Cleaning the screen and setting the background
    glEnable(GL_BLEND)
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader)

    try:
        mouse_pos = mouse.get_mouse_pos(screen)

        block_pos = game_field.get_block_field_position(*mouse_pos)

        y = block_pos.y * BLOCK_SIZE
        x1 = block_pos.x * BLOCK_SIZE
        x2 = GAME_FIELD_WIDTH - x1 - BLOCK_SIZE

        # Use a square geometry at origin and place it using uPlayerPos uniform
        square_vertices = OpenGLUtils.create_square_vertices(BLOCK_SIZE)
        block_vao, block_vbo = renderer.create_vao_vbo(square_vertices)
        # Configure vertex attribute for position (location 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        renderer.draw_rect(
            block_vao,
            uUseTexture=(uUseTextureLoc, False),
            uIsPlayer=(uIsPlayerLoc, True),
            uPlayerPos=uPlayerPos,
            uColor=uColorLoc,
            rect=FloatRect(x1, y, BLOCK_SIZE, BLOCK_SIZE),
            color=VIRTUAL_BLOCK_COLOR
        )

        renderer.draw_rect(
            block_vao,
            uUseTexture=(uUseTextureLoc, False),
            uIsPlayer=(uIsPlayerLoc, True),
            uPlayerPos=uPlayerPos,
            uColor=uColorLoc,
            rect=FloatRect(x2, y, BLOCK_SIZE, BLOCK_SIZE),
            color=VIRTUAL_BLOCK_COLOR
        )

    except IndexError:
        ...

    for rect, (vao, vbo) in lines.items():
        renderer.draw_rect(
            vao,
            uUseTexture=(glGetUniformLocation(shader, "uUseTexture"), False),
            uIsPlayer=(glGetUniformLocation(shader, "uIsPlayer"), False),
            uPlayerPos=None,
            uColor=glGetUniformLocation(shader, "uColor"),
            rect=rect,
            color=MAPS_CELLS_COLOR
        )

    # Draw
    game_field.draw()

    clock.tick(60)
    pygame.display.flip()
