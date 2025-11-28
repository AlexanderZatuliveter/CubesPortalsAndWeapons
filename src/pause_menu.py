import sys
import numpy as np
import pygame
from OpenGL.GL import *  # type: ignore
from OpenGL.GLU import *  # type: ignore

from button import Button
from consts import BUTTON_HEIGHT, BUTTON_OFFSET, BUTTON_WIDTH, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from float_rect import FloatRect
from music_manager import MusicManager


class PauseMenu:
    def __init__(self, shader, music_manager: MusicManager) -> None:

        # make background
        self.rect = FloatRect(0.0, 0.0, GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT)

        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uColor = glGetUniformLocation(shader, "uColor")

        vertices = np.array([
            0.0, 0.0,
            GAME_FIELD_WIDTH, 0.0,
            GAME_FIELD_WIDTH, GAME_FIELD_HEIGHT,
            0.0, GAME_FIELD_HEIGHT,
        ], dtype=np.float32)

        self.__vertex_count = 4

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # This makes it an instance attribute

        # make buttons
        self.__buttons: list[Button] = []

        buttons = {
            "Continue": self.__start_button_func,
            "Options": None,
            "Exit to Main Menu": None,
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
                shader,
                list(buttons.values())[i]
            )

            self.__buttons.append(button)

        self.__is_active = False

        self.__music_manager = music_manager

    def __background_draw(self) -> None:
        glBindVertexArray(self.__vao)
        glUniform1i(self.__uUseTexture, 0)
        glUniform1i(self.__uIsPlayer, 0)
        glUniform3f(self.__uColor, 0.1, 0.1, 0.1)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)

    def show(self) -> None:
        self.__is_active = True

        self.__music_manager.play_pause_music()

        while self.__is_active:
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
                        self.__is_active = False
                        break

            # Обновление кнопок
            for button in self.__buttons:
                button.update(mouse_pos, mouse_pressed)

            self.__background_draw()

            for button in self.__buttons:
                button.draw()

            pygame.display.flip()

    def is_active(self) -> bool:
        return self.__is_active

    def __start_button_func(self) -> None:
        self.__is_active = False

    def __desktop_exit_button_func(self) -> None:
        pygame.quit()
        sys.exit()
