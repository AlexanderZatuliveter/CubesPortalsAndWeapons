from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import ShaderProgram
import numpy as np
import ctypes
import pygame

from engine.common import get_resource_path
from game.consts import BLUE, BUTTON_HEIGHT, BUTTON_WIDTH, GREY, GREY_2, ORANGE, WHITE
from engine.ui.text_worker import TextWorker


class Button:
    def __init__(self, x: float, y: float, text: str, shader: ShaderProgram | None, function) -> None:
        self.__rect: pygame.Rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.__text = text
        self.__color = GREY
        self.__prev_pressed = False

        self.__active = False
        self.__joy_active = False
        self.__joy_current_button = False

        self.__function = function

        # Shader uniform locations
        self.__uColor = glGetUniformLocation(shader, "uColor")
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")

        # Background quad (uses positions in screen/game units)
        vertices = np.array([
            0.0, 0.0,
            BUTTON_WIDTH, 0.0,
            BUTTON_WIDTH, BUTTON_HEIGHT,
            0.0, BUTTON_HEIGHT,
        ], dtype=np.float32)

        self.__vertex_count = 4

        # VAO/VBO for background rectangle
        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        self.__vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        # Dynamic offset buffer (we'll update it per-draw)
        self.__offset_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        offset_data = np.array([0.0, 0.0], dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, offset_data.nbytes, offset_data, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # keeps backwards compatibility with instanced usage

        glBindVertexArray(0)

        self.__text_worker = TextWorker(
            x=self.__rect.x,
            y=self.__rect.y + BUTTON_HEIGHT * 0.25,
            text=self.__text,
            rect_size=(self.__rect.width, self.__rect.height * 0.5),
            font=None,
            font_file_path=get_resource_path("src/_content/fonts/Orbitron-VariableFont_wght.ttf"),
            shader=shader,
            color=WHITE
        )

    def update(self, mouse_pos: tuple[int, int], mouse_pressed: tuple[bool, bool, bool]) -> None:

        # MOUSE
        left = mouse_pressed[0]

        mouse_down = left and not self.__prev_pressed
        mouse_up = not left and self.__prev_pressed

        if self.__rect.collidepoint(mouse_pos):
            if mouse_down:
                self.__color = BLUE
                self.__active = True
            elif not self.__active:
                self.__color = ORANGE
        else:
            if not self.__active:
                self.__color = GREY_2

        if mouse_up and self.__active:
            self.__active = False
            self.__perform_function()

        self.__prev_pressed = left

        # JOYSTICK
        if self.__joy_current_button:
            self.__color = ORANGE

        if self.__joy_active:
            self.__color = BLUE
            self.__joy_current_button = self.__joy_active = False
            self.__perform_function()

        if not self.__joy_current_button:
            self.__color = GREY_2

    def draw(self) -> None:
        glBindVertexArray(self.__vao)

        # update offset for background
        offset = np.array([float(self.__rect.x), float(self.__rect.y)], dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.__offset_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, offset.nbytes, offset)

        glUniform1i(self.__uIsPlayer, 0)
        glUniform1i(self.__uUseTexture, 0)
        # send RGBA with alpha=1.0
        glUniform4f(self.__uColor, *self.__color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.__vertex_count)
        glBindVertexArray(0)

        self.__text_worker.draw()

    def __perform_function(self) -> None:
        if self.__function is None:
            return
        self.__function()

    def set_current_button(self) -> None:
        self.__joy_current_button = True

    def unset_current_button(self) -> None:
        self.__joy_current_button = False

    def is_current(self) -> bool:
        return self.__joy_current_button

    def set_active(self) -> None:
        self.__joy_active = True
