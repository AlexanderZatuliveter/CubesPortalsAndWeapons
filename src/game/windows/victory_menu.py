import sys
import pygame
from pygame.event import Event
from pygame import Surface
from pygame.time import Clock
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from engine.ui.button import Button
from engine.common import get_resource_path
from game.consts import BLUE, BUTTON_HEIGHT, BUTTON_OFFSET, BUTTON_WIDTH, MENU_BG_COLOR, MENU_FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, GREEN, ORANGE, RED, VICTORY_TEXT_HEIGHT, VICTORY_TEXT_WIDTH
from engine.graphics.display_manager import DisplayManager
from engine.joysticks_manager import JoysticksManager
from game.systems.game_state import GameState
from engine.music_manager import MusicManager
from engine.graphics.opengl_utils import OpenGLUtils
from engine.shader_utils import ShaderUtils
from engine.ui.text_worker import TextWorker
from game.enums.window_enum import WindowEnum


class VictoryMenu:
    def __init__(
        self,
        winner_color: tuple[float, float, float, float],
        game_state: GameState,
        screen: Surface,
        clock: Clock,
        music_manager: MusicManager,
        joysticks_manager: JoysticksManager
    ) -> None:

        self.__game_state = game_state
        self.__joysticks_manager = joysticks_manager
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()

        self.__winner_color = winner_color

        # Enable alpha blending by default for UI and textures
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.__shader = ShaderUtils.create_shader(
            "./src/game/_shaders/2d_shader.vert",
            "./src/game/_shaders/2d_shader.frag")
        glUseProgram(self.__shader)

        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

        # make buttons
        self.__buttons: list[Button] = []

        buttons = {
            "Restart": self.__restart_button_func,
            "Exit to Main Menu": self.__main_menu_button_func,
            "Exit to Desktop": self.__desktop_exit_button_func
        }

        start_y = GAME_FIELD_HEIGHT / 3 * 2 - BUTTON_HEIGHT * \
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

        self.__rect = pygame.rect.Rect(
            GAME_FIELD_WIDTH / 2 - VICTORY_TEXT_WIDTH * 0.5,
            GAME_FIELD_HEIGHT / 3.5 - VICTORY_TEXT_HEIGHT * 0.5,
            VICTORY_TEXT_WIDTH,
            VICTORY_TEXT_HEIGHT
        )

        for consts_color in [BLUE, RED, GREEN, ORANGE]:
            if consts_color == self.__winner_color:
                for name, value in globals().items():
                    if value is consts_color:
                        self.__text = f"{name} PLAYER WIN"

        self.__text_worker = TextWorker(
            x=self.__rect.x,
            y=self.__rect.y + BUTTON_HEIGHT * 0.25,
            text=self.__text,
            rect_size=(self.__rect.width, self.__rect.height * 0.5),
            font=None,
            font_file_path=get_resource_path("src/_content/fonts/Orbitron-VariableFont_wght.ttf"),
            shader=self.__shader,
            color=self.__winner_color
        )

        self.__display_manager = DisplayManager()
        self.__music_manager = music_manager

        self.__running = True

    def show(self) -> None:

        self.__screen = self.__display_manager.set_screen_size(self.__screen, self.__shader, self.__screen.get_size())

        # Set background's color
        glClearColor(*MENU_BG_COLOR)

        self.__music_manager.play_victory_menu_music()
        self.__running = True

        self.__joysticks_manager.current_first_button(self.__buttons)

        while self.__running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            self.update(events)
            self.__joysticks_manager.update_joystick_selection(events, self.__buttons)

            scale = self.__screen.get_width() / pygame.display.get_window_size()[0]
            mouse_pos = (int(mouse_pos[0] * scale), int(mouse_pos[1] * scale))

            for button in self.__buttons:
                button.update()

            # Draws
            glDisable(GL_DEPTH_TEST)

            glEnable(GL_BLEND)

            glClear(GL_COLOR_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.__shader)

            for button in self.__buttons:
                button.draw()

            self.__text_worker.draw()

            pygame.display.flip()
            self.__clock.tick(MENU_FPS)

    def update(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__game_state.current_window = WindowEnum.GAME_WINDOW
                    self.__running = False
            if event.type == pygame.VIDEORESIZE:
                videoresize = self.__display_manager.resize_display(
                    self.__screen, self.__shader, self.__past_screen_size, event.size)

                if videoresize is not None:
                    self.__screen, self.__past_screen_size = videoresize

    def __desktop_exit_button_func(self) -> None:
        pygame.quit()
        sys.exit()

    def __restart_button_func(self) -> None:
        self.__game_state.current_window = WindowEnum.GAME_WINDOW
        self.__running = False

    def __main_menu_button_func(self) -> None:
        self.__game_state.current_window = WindowEnum.MAIN_MENU
        self.__running = False
