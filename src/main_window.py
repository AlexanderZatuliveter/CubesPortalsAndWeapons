
import sys
from typing import Tuple
import numpy as np
import pygame
from pygame.event import Event
from pygame import Surface
from pygame.time import Clock
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from bullets import Bullets
from common import create_shader, ortho
from consts import BLOCK_SIZE, FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, BLUE, ORANGE, RED, GREEN
from game_field import GameField
from player import Player


class MainWindow:

    def __init__(self, screen: Surface, clock: Clock) -> None:
        self.__screen = screen
        self.__clock = clock
        self.__past_screen_size = self.__screen.get_size()

        # Disable unnecessary OpenGL features for 2D rendering
        glDisable(GL_DEPTH_TEST)  # No depth testing needed for 2D
        glDisable(GL_CULL_FACE)   # No backface culling needed
        glDisable(GL_MULTISAMPLE)  # No multisampling needed for pixel-perfect 2D

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

        self.__colors = [BLUE, RED, GREEN, ORANGE]

        self.__players: dict[Player, int] = {}

        self.__bullets = Bullets(list(self.__players.keys()), self.__game_field)

    def __resize_display(self, new_screen_size: Tuple[int, int]) -> None:
        """Handle window resizing while maintaining the aspect ratio."""

        if self.__past_screen_size == new_screen_size:
            return

        ratio_w = new_screen_size[0] / GAME_FIELD_WIDTH
        ratio_h = new_screen_size[1] / GAME_FIELD_HEIGHT

        if self.__past_screen_size[0] != new_screen_size[0] and self.__past_screen_size[1] != new_screen_size[1]:
            ratio = min(ratio_w, ratio_h)
        elif self.__past_screen_size[0] != new_screen_size[0]:
            ratio = ratio_w
        elif self.__past_screen_size[1] != new_screen_size[1]:
            ratio = ratio_h

        new_width = int(GAME_FIELD_WIDTH * ratio)
        new_height = int(GAME_FIELD_HEIGHT * ratio)

        self.__set_screen_size((new_width, new_height))

        self.__past_screen_size = pygame.display.get_window_size()

    def __set_screen_size(self, screen_size: Tuple[int, int]) -> None:
        # Set up the viewport to maintain aspect ratio
        self.__screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
        glViewport(0, 0, *screen_size)

        # Update the projection matrix in the shader
        glUseProgram(self.__shader)
        uProjection = glGetUniformLocation(self.__shader, "uProjection")
        self.__projection = ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, self.__projection.T)

    def show(self) -> None:

        self.__set_screen_size(self.__screen.get_size())

        # Set background's color
        glClearColor(120 / 255, 120 / 255, 120 / 255, 1)

        while True:

            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            # self.__add_player()

            # Updates
            self.update(events)

            for player in self.__players.keys():
                player.update()

            self.__bullets.update()

            # Draws
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.__shader)

            self.__game_field.draw()

            for player in self.__players.keys():
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
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.__resize_display(event.size)

            if event.type == pygame.JOYDEVICEADDED:
                print("JOYDEVICEADDED")

                for player_key, player_value in self.__players.items():
                    print(f"check player values: key={player_key}, value={player_value}")
                    if player_value == 0:
                        joystick = pygame.joystick.Joystick(len(self.__players) - 1)
                        if "Receiver" in joystick.get_name():
                            print("return, Receiver in joy_name #1")
                            return
                        joystick.init()
                        self.__players[player_key] = id(joystick)
                        list(self.__players.keys())[list(self.__players.keys()).index(
                            player_key)].update_joystick(joystick)
                        print(f"{list(self.__players.keys())[list(self.__players.keys()).index(
                            player_key)]=}")
                        print(f"new player value: key={player_key}, value={self.__players[player_key]}")
                        print(f"{self.__players=}")
                        return

                print(f"last_{len(self.__players)=}")
                if len(self.__players) > 0:
                    joystick = pygame.joystick.Joystick(len(self.__players) - 1)
                    color_index = len(self.__players) - 1
                else:
                    joystick = pygame.joystick.Joystick(0)
                    color_index = 0

                print(f"joy_name={joystick.get_name()}")
                if "Receiver" in joystick.get_name():
                    print("return, Receiver in joy_name #2")
                    return

                joy_id = id(joystick)
                print(f"{joy_id=}")
                if joy_id in self.__players.values():
                    print(f"{joy_id} in self.__players ids")
                    return

                joystick.init()

                self.__players[Player(
                    self.__game_field,
                    self.__shader,
                    self.__colors[color_index],
                    joystick,
                    self.__bullets
                )] = joy_id

                print(f"{self.__players=}")

            if event.type == pygame.JOYDEVICEREMOVED:
                print("JOYDEVICEREMOVED")
                self.__players[list(self.__players.keys())[0]] = 0
                print(f"{self.__players=}")
