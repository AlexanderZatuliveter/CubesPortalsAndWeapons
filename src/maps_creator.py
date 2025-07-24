import sys
from typing import Tuple
import pygame
from consts import BLOCK_SIZE, GAME_FIELD_HEIGHT, GAME_FIELD_PROPORTIONS, GAME_FIELD_WIDTH
from mouse_buttons import Mouse
from game_field import GameField
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE, VIDEORESIZE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore


pygame.init()


bg_color = 200, 200, 200

info = pygame.display.Info()
target_width = int(info.current_w * 0.8)
target_height = int(target_width / GAME_FIELD_PROPORTIONS)
screen_size = (target_width, target_height)

# Создаём окно с поддержкой OpenGL
screen: pygame.Surface = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)

mouse = Mouse()
game_field = GameField(GAME_FIELD_WIDTH // BLOCK_SIZE, GAME_FIELD_HEIGHT // BLOCK_SIZE)
clock = pygame.time.Clock()


def set_screen_size(screen_size: Tuple[int, int]) -> None:
    glViewport(0, 0, *screen_size)

    # Reset projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT, 0, -1, 1)


# Настройка OpenGL один раз после создания окна
set_screen_size(screen_size)

# # Включаем сглаживание линий и альфа-смешивание
# glEnable(GL_LINE_SMOOTH)
# glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
# glEnable(GL_BLEND)
# glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


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

        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, DOUBLEBUF | OPENGL | RESIZABLE)
            set_screen_size(event.size)

    # Очистка экрана и установка фона
    glClearColor(100 / 255, 100 / 255, 100 / 255, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Отрисовка
    glBegin(GL_QUADS)
    game_field.draw()
    glEnd()

    mouse.update(game_field)

    clock.tick(60)
    pygame.display.flip()
