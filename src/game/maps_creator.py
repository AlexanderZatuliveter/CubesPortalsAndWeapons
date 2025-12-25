import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from game_field import GameField
from mouse_buttons import Mouse
from game.consts import BG_COLOR, BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_PROPORTIONS, GAME_FIELD_WIDTH
from engine.shader_utils import ShaderUtils
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.display_manager import DisplayManager

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

shader = ShaderUtils.create_shader("./src/game/_shaders/shader.vert", "./src/game/_shaders/shader.frag")
glUseProgram(shader)

uProjection = glGetUniformLocation(shader, "uProjection")
projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection.T)

mouse = Mouse()
game_field = GameField(
    int(GAME_FIELD_WIDTH // BLOCK_SIZE),
    int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
    shader
)
clock = pygame.time.Clock()

display_manager = DisplayManager()


# Настройка OpenGL один раз после создания окна
screen = display_manager.set_screen_size(screen, shader, screen.get_size())

# Set background's color
glClearColor(*BG_COLOR, 1)


while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if keys[pygame.K_ESCAPE] or event.type == pygame.QUIT:
            print(f"blocks:{mouse.blocks}")
            pygame.quit()
            sys.exit()

        if keys[pygame.K_s]:
            print('saved')
            game_field.save_to_file()

        if keys[pygame.K_l]:
            print('loaded')
            game_field.load_from_file()

        if event.type == pygame.VIDEORESIZE:
            videoresize = display_manager.resize_display(screen, shader, past_screen_size, event.size)

            if videoresize is not None:
                screen, past_screen_size = videoresize

    # Очистка экрана и установка фона
    glEnable(GL_BLEND)
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader)

    # === Отрисовка ===
    game_field.draw()
    mouse.update(game_field)

    clock.tick(60)
    pygame.display.flip()
