
import sys
import time
import numpy as np
import pygame
from pygame.event import Event
from pygame import Surface

from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from game.systems.bullets import Bullets
from game.consts import GAME_BG_COLOR, BLOCK_SIZE, DRAW_DT, UPDATE_DT, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from engine.joysticks_manager import JoysticksManager
from game.systems.damage import Damage
from engine.graphics.display_manager import DisplayManager
from game.game_field import GameField
from game.systems.game_state import GameState
from engine.music_manager import MusicManager
from engine.graphics.opengl_utils import OpenGLUtils
from engine.graphics.opengl_3d_utils import OpenGL_3D_Utils
from game.systems.players import Players
from engine.shader_utils import ShaderUtils
from game.enums.window_enum import WindowEnum
from game.systems.weapons import Weapons


class GameWindow:

    def __init__(
        self,
        game_state: GameState,
        screen: Surface,
        music_manager: MusicManager,
        joysticks_manager: JoysticksManager
    ) -> None:

        self.__game_state = game_state
        self.__screen = screen
        self.__past_screen_size = self.__screen.get_size()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Disable unnecessary OpenGL features for 2D rendering
        glDisable(GL_DEPTH_TEST)  # No depth testing needed for 2D
        glDisable(GL_CULL_FACE)   # No backface culling needed
        glDisable(GL_MULTISAMPLE)  # No multisampling needed for pixel-perfect 2D

        # Enable alpha blending by default for UI and textures
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.__2d_shader = ShaderUtils.create_shader(
            "./src/game/_shaders/2d_shader.vert",
            "./src/game/_shaders/2d_shader.frag")
        glUseProgram(self.__2d_shader)

        u2dProjection = glGetUniformLocation(self.__2d_shader, "uProjection")
        self.__2d_projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(u2dProjection, 1, GL_FALSE, self.__2d_projection.T)

        self.__3d_shader = ShaderUtils.create_shader(
            "./src/game/_shaders/3d_shader.vert",
            "./src/game/_shaders/3d_shader.frag")
        glUseProgram(self.__3d_shader)

        u3dProjection = glGetUniformLocation(self.__3d_shader, "uProjection")
        self.__3d_projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -150, 150)
        glUniformMatrix4fv(u3dProjection, 1, GL_FALSE, self.__3d_projection.T)

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
            self.__2d_shader
        )

        # Load map first so block positions are available for weapon placement
        self.__game_field.load_from_file("third.map")

        self.__bullets = Bullets()
        self.__players = Players(self.__game_field, joysticks_manager, self.__2d_shader, self.__bullets)
        self.__damage = Damage(self.__players, self.__bullets, self.__game_field)
        self.__weapons = Weapons(self.__game_field, self.__3d_shader, self.__2d_shader)

        self.__display_manager = DisplayManager()
        self.__music_manager = music_manager

        self.__running = True

    def show(self) -> None | tuple[float, float, float, float]:

        self.__screen = self.__display_manager.set_screen_size(
            self.__screen, self.__2d_shader, self.__screen.get_size())

        self.__music_manager.play_game_theme()
        self.__running = True

        last_time = time.perf_counter()
        update_accumulator = 0.0
        draw_accumulator = 0.0

        start = time.time()

        light_pos = np.array([GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2, 100], dtype=np.float32)
        camera_pos = np.array([0.0, 0.0, 50], dtype=np.float32)

        glClearColor(*GAME_BG_COLOR)

        while self.__running:
            t = time.time() - start

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
                self.__damage.update(UPDATE_DT)

                for player in self.__players:
                    if player.get_scores() >= 25:
                        self.__game_state.current_window = WindowEnum.VICTORY_MENU
                        return player._color

                for weapon in self.__weapons:
                    for player in self.__players:
                        if player.rect.colliderect(weapon.rect):
                            player.update_weapon(weapon.get_type())
                            self.__weapons.remove(weapon)

                update_accumulator -= UPDATE_DT

            # Draws
            while draw_accumulator >= DRAW_DT:
                view = OpenGLUtils.look_at(
                    np.array([0.0, 0.0, 50], dtype=np.float32),  # Позиция камеры
                    np.array([0.0, 0.0, 0.0], dtype=np.float32),  # Куда смотрит (в центр)
                    np.array([0.0, 1.0, 0.0], dtype=np.float32)  # Где "верх" (ось Y)
                )

                glEnable(GL_DEPTH_TEST)

                glEnable(GL_BLEND)
                glClear(GL_COLOR_BUFFER_BIT)
                glClear(GL_DEPTH_BUFFER_BIT)

                glUseProgram(self.__3d_shader)

                self.__weapons.draw(self.__3d_projection, view, t, light_pos, camera_pos)

                glUseProgram(self.__2d_shader)

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or \
                    (event.type == pygame.JOYBUTTONDOWN and event.button == 7):
                self.__game_state.current_window = WindowEnum.PAUSE_MENU
                self.__running = False
            if event.type == pygame.VIDEORESIZE:
                videoresize = self.__display_manager.resize_display(
                    self.__screen, self.__2d_shader, self.__past_screen_size, event.size)

                if videoresize is not None:
                    self.__screen, self.__past_screen_size = videoresize
