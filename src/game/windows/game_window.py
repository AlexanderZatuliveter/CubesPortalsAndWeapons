
import sys
import time
import numpy as np
import pygame
from pygame.event import Event
from pygame import Surface

from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from game.entities.buff import Buff
from game.entities.weapon import Weapon
from game.systems.bullets import Bullets
from game.consts import GAME_BG_COLOR, BLOCK_SIZE, DRAW_DT, UPDATE_DT, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from engine.joysticks_manager import JoysticksManager
from game.systems.collectable_objects import CollectableObjects
from game.systems.damage import Damage
from engine.graphics.display_manager import DisplayManager
from game.game_field import GameField
from game.systems.game_state import GameState
from engine.music_manager import MusicManager
from engine.graphics.opengl_utils import OpenGLUtils
from game.systems.players import Players
from engine.shader_utils import ShaderUtils
from game.enums.window_enum import WindowEnum


class GameWindow:

    def __init__(
        self,
        game_state: GameState,
        screen: Surface,
        music_manager: MusicManager,
        joysticks_manager: JoysticksManager,
        map_path: str,
        player_start_pos: tuple[float, float]
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

        u2dProjection = glGetUniformLocation(self.__2d_shader, "uProjection")
        self.__2d_projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(u2dProjection, 1, GL_FALSE, self.__2d_projection.T)

        self.__3d_shader = ShaderUtils.create_shader(
            "./src/game/_shaders/3d_shader.vert",
            "./src/game/_shaders/3d_shader.frag")

        u3dProjection = glGetUniformLocation(self.__3d_shader, "uProjection")
        self.__3d_projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -150, 150)
        glUniformMatrix4fv(u3dProjection, 1, GL_FALSE, self.__3d_projection.T)

        # Cache 3D shader uniform locations for faster rendering
        self.__3d_uniforms = {
            "mvp": glGetUniformLocation(self.__3d_shader, "mvp"),
            "model": glGetUniformLocation(self.__3d_shader, "model"),
            "lightPos": glGetUniformLocation(self.__3d_shader, "lightPos"),
            "viewPos": glGetUniformLocation(self.__3d_shader, "viewPos"),
            "objectColor": glGetUniformLocation(self.__3d_shader, "objectColor"),
        }

        self.__view = OpenGLUtils.look_at(
            np.array([0.0, 0.0, 50], dtype=np.float32),
            np.array([0.0, 0.0, 0.0], dtype=np.float32),
            np.array([0.0, 1.0, 0.0], dtype=np.float32)
        )

        self.__game_field = GameField(
            int(GAME_FIELD_WIDTH // BLOCK_SIZE),
            int(GAME_FIELD_HEIGHT // BLOCK_SIZE),
            self.__2d_shader
        )

        self.__game_field.load_from_file(map_path)

        self.__bullets = Bullets()
        self.__players = Players(
            self.__game_field,
            joysticks_manager,
            self.__2d_shader,
            self.__bullets,
            player_start_pos
        )
        self.__damage = Damage(self.__players, self.__bullets, self.__game_field)
        self.__collectable_objects = CollectableObjects(self.__game_field, self.__3d_shader)

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

            self.update_events(events)

            # Updates
            while update_accumulator >= UPDATE_DT:
                self.__players.update(events, UPDATE_DT)
                self.__damage.update(UPDATE_DT)

                for player in self.__players:
                    if player.get_scores() >= 25:
                        self.__game_state.current_window = WindowEnum.VICTORY_MENU
                        return player._color

                for object in self.__collectable_objects:
                    for player in self.__players:
                        if player.rect.colliderect(object.rect):
                            if isinstance(object, Weapon):
                                player.update_weapon(object.get_type())
                            elif isinstance(object, Buff):
                                player.set_buff(object.get_type())
                            self.__collectable_objects.remove(object)

                update_accumulator -= UPDATE_DT

            # Draws
            while draw_accumulator >= DRAW_DT:
                glEnable(GL_DEPTH_TEST)

                glEnable(GL_BLEND)
                glClear(GL_COLOR_BUFFER_BIT)
                glClear(GL_DEPTH_BUFFER_BIT)

                # --- 2D Rendering Pass ---
                glUseProgram(self.__2d_shader)
                glDisable(GL_DEPTH_TEST)

                self.__game_field.draw()

                for player in self.__players:
                    player.draw()

                self.__bullets.draw()

                # --- 3D Rendering Pass ---
                glUseProgram(self.__3d_shader)
                glEnable(GL_DEPTH_TEST)

                self.__collectable_objects.draw(
                    self.__3d_projection,
                    self.__view,
                    t,
                    light_pos,
                    camera_pos,
                    self.__3d_uniforms
                )

                pygame.display.flip()

                draw_accumulator -= DRAW_DT

    def update_events(self, events: list[Event]) -> None:
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
