
import sys
import pygame
from pygame.event import Event
from pygame import Surface
from pygame.time import Clock

from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from bullets import Bullets
from common import create_shader, ortho, resize_display, set_screen_size
from consts import BG_COLOR, BLOCK_SIZE, FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from damage import Damage
from game_field import GameField
from game_state import GameState
from music_manager import MusicManager
from players import Players
from window_enum import WindowEnum


class GameWindow:

    def __init__(self, game_state: GameState, screen: Surface, clock: Clock, music_manager: MusicManager) -> None:
        self.__game_state = game_state
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()

        # Disable unnecessary OpenGL features for 2D rendering
        glDisable(GL_DEPTH_TEST)  # No depth testing needed for 2D
        glDisable(GL_CULL_FACE)   # No backface culling needed
        glDisable(GL_MULTISAMPLE)  # No multisampling needed for pixel-perfect 2D
        # Enable alpha blending by default for UI and textures
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.__shader = create_shader("./src/shaders/shader.vert", "./src/shaders/shader.frag")
        glUseProgram(self.__shader)

        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
            self.__shader
        )

        self.__game_field.load_from_file()

        self.__bullets = Bullets()
        self.__players = Players(self.__game_field, self.__shader, self.__bullets)
        self.__damage = Damage(self.__players, self.__bullets, self.__game_field)

        self.__music_manager = music_manager

        self.__running = True

    def show(self) -> None:

        self.__screen = set_screen_size(self.__screen, self.__shader, self.__screen.get_size())

        # Set background's color
        glClearColor(*BG_COLOR, 1)

        self.__music_manager.play_game_theme()
        self.__running = True

        while self.__running:

            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # Updates
            self.update(events)

            self.__players.update(events)

            self.__damage.update()

            # Draws
            glEnable(GL_BLEND)
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.__shader)

            self.__game_field.draw()

            for player in self.__players:
                player.draw()

            self.__bullets.draw()

            pygame.display.flip()
            self.__clock.tick(FPS)

    def update(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__game_state.current_window = WindowEnum.PAUSE_MENU
                    self.__running = False
            if event.type == pygame.VIDEORESIZE:
                videoresize = resize_display(self.__screen, self.__shader, self.__past_screen_size, event.size)

                if videoresize is not None:
                    self.__screen, self.__past_screen_size = videoresize
