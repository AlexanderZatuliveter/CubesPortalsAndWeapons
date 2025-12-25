import sys
import pygame
from pygame.event import Event
from pygame import Surface
from pygame.time import Clock
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from engine.ui.button import Button
from game.consts import BUTTON_HEIGHT, BUTTON_OFFSET, BUTTON_WIDTH, FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from engine.graphics.display_manager import DisplayManager
from game.systems.game_state import GameState
from engine.music_manager import MusicManager
from engine.graphics.opengl_utils import OpenGLUtils
from engine.shader_utils import ShaderUtils
from game.enums.window_enum import WindowEnum


class MainMenu:
    def __init__(self, game_state: GameState, screen: Surface, clock: Clock, music_manager: MusicManager) -> None:
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()
        self.__game_state = game_state

        # Enable alpha blending by default for UI and textures
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.__shader = ShaderUtils.create_shader("./src/game/_shaders/shader.vert", "./src/game/_shaders/shader.frag")
        glUseProgram(self.__shader)

        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

        # make buttons
        self.__buttons: list[Button] = []

        buttons = {
            "Start": self.__start_button_func,
            "Options": None,
            "Exit to Desktop": self.__desktop_exit_button_func
        }

        start_y = GAME_FIELD_HEIGHT / 2 - BUTTON_HEIGHT * \
            len(buttons) // 2 - BUTTON_OFFSET * len(buttons) // 2 - BUTTON_OFFSET * 0.5

        button_x = GAME_FIELD_WIDTH / 2 - BUTTON_WIDTH / 2

        for i in range(len(buttons)):
            button_y = start_y + (BUTTON_HEIGHT + BUTTON_OFFSET) * i

            button = Button(
                button_x,
                button_y,
                list(buttons.keys())[i],
                self.__shader,
                list(buttons.values())[i]
            )

            self.__buttons.append(button)

        self.__display_manager = DisplayManager()
        self.__music_manager = music_manager

        self.__running = True

    def show(self) -> None:

        self.__screen = self.__display_manager.set_screen_size(self.__screen, self.__shader, self.__screen.get_size())

        # Set background's color
        glClearColor(0.1, 0.1, 0.1, 1)

        self.__music_manager.play_main_menu_music()
        self.__running = True

        while self.__running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break

            self.update(events)

            scale = self.__screen.get_width() / pygame.display.get_window_size()[0]
            mouse_pos = (int(mouse_pos[0] * scale), int(mouse_pos[1] * scale))

            for button in self.__buttons:
                button.update(mouse_pos, mouse_pressed)

            # Draws
            glEnable(GL_BLEND)
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.__shader)

            for button in self.__buttons:
                button.draw()

            pygame.display.flip()
            self.__clock.tick(FPS)

    def update(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                videoresize = self.__display_manager.resize_display(
                    self.__screen, self.__shader, self.__past_screen_size, event.size)

                if videoresize is not None:
                    self.__screen, self.__past_screen_size = videoresize

    def __desktop_exit_button_func(self) -> None:
        pygame.quit()
        sys.exit()

    def __start_button_func(self) -> None:
        self.__game_state.current_window = WindowEnum.GAME_WINDOW
        self.__running = False
