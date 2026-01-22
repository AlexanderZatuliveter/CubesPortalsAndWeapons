import sys
import pygame
from abc import ABC, abstractmethod
from pygame import Surface
from pygame.event import Event
from pygame.time import Clock
from OpenGL.GL import *  # type: ignore

from engine.graphics.display_manager import DisplayManager
from engine.joysticks_manager import JoysticksManager
from engine.music_manager import MusicManager
from engine.shader_utils import ShaderUtils
from engine.graphics.opengl_utils import OpenGLUtils
from engine.ui.button import Button
from game.consts import BUTTON_HEIGHT, BUTTON_OFFSET, BUTTON_WIDTH, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT, MENU_BG_COLOR
from game.systems.game_state import GameState


class BaseMenu(ABC):
    def __init__(
        self,
        game_state: GameState,
        screen: Surface,
        clock: Clock,
        music_manager: MusicManager,
        joysticks_manager: JoysticksManager
    ) -> None:

        self._game_state = game_state
        self._screen = screen
        self._clock = clock
        self._music_manager = music_manager
        self._joysticks_manager = joysticks_manager
        self._past_screen_size = self._screen.get_size()
        self._display_manager = DisplayManager()
        self._running = True
        self._buttons: list[Button] = []

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._shader = ShaderUtils.create_shader(
            "./src/game/_shaders/2d_shader.vert",
            "./src/game/_shaders/2d_shader.frag"
        )

        glUseProgram(self._shader)
        uProjection = glGetUniformLocation(self._shader, "uProjection")
        self._projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self._projection.T)

    def _create_buttons(self, buttons: dict) -> list[Button]:
        buttons_list = []

        start_y = GAME_FIELD_HEIGHT / 2 - BUTTON_HEIGHT * \
            len(buttons) // 2 - BUTTON_OFFSET * len(buttons) // 2 - BUTTON_OFFSET * 0.5

        button_x = GAME_FIELD_WIDTH / 2 - BUTTON_WIDTH / 2

        for i in range(len(buttons)):
            button_y = start_y + (BUTTON_HEIGHT + BUTTON_OFFSET) * i

            button = Button(
                button_x,
                button_y,
                list(buttons.keys())[i],
                self._shader,
                list(buttons.values())[i]
            )

            buttons_list.append(button)

        return buttons_list

    def _update_common_events(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                videoresize = self._display_manager.resize_display(
                    self._screen, self._shader, self._past_screen_size, event.size)
                print(f"{videoresize=}")
                if videoresize is not None:
                    self._screen, self._past_screen_size = videoresize

            self._update_custom_events(event)

    @abstractmethod
    def _update_custom_events(self, event: Event) -> None:
        pass

    def _draw_base(self):
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glClearColor(*MENU_BG_COLOR)
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(self._shader)

        for button in self._buttons:
            button.draw()

    @abstractmethod
    def show(self):
        pass
