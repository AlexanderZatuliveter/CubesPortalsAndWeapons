
from OpenGL.GL.shaders import ShaderProgram
from OpenGL.GL import *  # type: ignore
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from game.consts import GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from engine.graphics.opengl_utils import OpenGLUtils


class DisplayManager:
    def set_screen_size(
        self,
        screen: pygame.Surface,
        shader: ShaderProgram | None,
        screen_size: tuple[int, int]
    ) -> pygame.Surface:
        # Set up the viewport to maintain aspect ratio
        screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
        glViewport(0, 0, *screen_size)

        # Update the projection matrix in the shader
        glUseProgram(shader)
        uProjection = glGetUniformLocation(shader, "uProjection")
        projection = OpenGLUtils.ortho(0, GAME_FIELD_WIDTH, 0, GAME_FIELD_HEIGHT, -1, 1)
        glUniformMatrix4fv(uProjection, 1, GL_FALSE, projection.T)

        return screen

    def resize_display(
        self,
        screen: pygame.Surface,
        shader: ShaderProgram | None,
        past_screen_size: tuple[float, float],
        new_screen_size: tuple[int, int]
    ) -> tuple[pygame.Surface, tuple[float, float]] | None:
        """Handle window resizing while maintaining the aspect ratio."""

        if past_screen_size == new_screen_size:
            return

        ratio_w = new_screen_size[0] / GAME_FIELD_WIDTH
        ratio_h = new_screen_size[1] / GAME_FIELD_HEIGHT

        if past_screen_size[0] != new_screen_size[0] and past_screen_size[1] != new_screen_size[1]:
            ratio = min(ratio_w, ratio_h)
        elif past_screen_size[0] != new_screen_size[0]:
            ratio = ratio_w
        elif past_screen_size[1] != new_screen_size[1]:
            ratio = ratio_h

        new_width = int(GAME_FIELD_WIDTH * ratio)
        new_height = int(GAME_FIELD_HEIGHT * ratio)

        screen = self.set_screen_size(screen, shader, (new_width, new_height))
        past_screen_size = pygame.display.get_window_size()

        return screen, past_screen_size
