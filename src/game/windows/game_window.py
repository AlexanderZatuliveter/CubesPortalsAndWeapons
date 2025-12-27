
import sys
import time
import pygame
from pygame.event import Event
from pygame import Surface
from pygame.time import Clock

from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from game.entities.bullets import Bullets
from game.consts import BG_COLOR, BLOCK_SIZE, DRAW_DT, UPDATE_DT, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from game.systems.damage import Damage
from engine.graphics.display_manager import DisplayManager
from game.game_field import GameField
from game.systems.game_state import GameState
from engine.music_manager import MusicManager
from engine.graphics.opengl_utils import OpenGLUtils
from game.entities.players import Players
from engine.shader_utils import ShaderUtils
from game.enums.window_enum import WindowEnum


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

        self.__shader = ShaderUtils.create_shader("./src/game/_shaders/shader.vert", "./src/game/_shaders/shader.frag")
        glUseProgram(self.__shader)

        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
            self.__shader
        )

        self.__game_field.load_from_file("third.map")

        self.__bullets = Bullets()
        self.__players = Players(self.__game_field, self.__shader, self.__bullets)
        self.__damage = Damage(self.__players, self.__bullets, self.__game_field)

        self.__display_manager = DisplayManager()
        self.__music_manager = music_manager

        self.__running = True

    def show(self) -> None | tuple[float, float, float]:

        self.__screen = self.__display_manager.set_screen_size(self.__screen, self.__shader, self.__screen.get_size())

        # Set background's color
        glClearColor(*BG_COLOR, 1)

        self.__music_manager.play_game_theme()
        self.__running = True

        last_time = time.perf_counter()
        update_accumulator = 0.0
        draw_accumulator = 0.0

        while self.__running:
            now = time.perf_counter()
            frame_time = now - last_time
            last_time = now

            update_accumulator += frame_time
            draw_accumulator += frame_time

            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            self.update(events)

            # Updates
            while update_accumulator >= UPDATE_DT:
                self.__players.update(events, UPDATE_DT)
                self.__damage.update()

                for player in self.__players:
                    if player.get_scores() >= 25:
                        self.__game_state.current_window = WindowEnum.VICTORY_MENU
                        return player._color

                update_accumulator -= UPDATE_DT

            # Draws
            while draw_accumulator >= DRAW_DT:
                glEnable(GL_BLEND)
                glClear(GL_COLOR_BUFFER_BIT)
                glUseProgram(self.__shader)

                self.__game_field.draw()

                for player in self.__players:
                    player.draw()

                self.__bullets.draw()

                pygame.display.flip()

                draw_accumulator -= DRAW_DT

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
                videoresize = self.__display_manager.resize_display(
                    self.__screen, self.__shader, self.__past_screen_size, event.size)

                if videoresize is not None:
                    self.__screen, self.__past_screen_size = videoresize
