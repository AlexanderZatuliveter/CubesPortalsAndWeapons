
from OpenGL.GL import *  # type: ignore
import numpy as np
from game.systems.float_rect import FloatRect


class Renderer2D:
    def create_vao_vbo(self, vertices: np.ndarray) -> tuple[int, int]:
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        return vao, vbo

    def draw_rect(
        self,
        vao,
        uUseTexture: tuple[int, bool],
        uIsPlayer: tuple[int, bool] | None,
        uPlayerPos: int | None,
        uColor: int,
        rect: FloatRect,
        color: tuple[float, float, float, float],
        vertex_count: int = 4
    ) -> None:

        glBindVertexArray(vao)
        glUniform1i(uUseTexture[0], uUseTexture[1])

        if uIsPlayer:
            glUniform1i(uIsPlayer[0], 1 if uIsPlayer[1] else 0)
            if uIsPlayer[1] and uPlayerPos is not None:
                glUniform2f(uPlayerPos, rect.x, rect.y)

        glUniform4f(uColor, *color)
        glDrawArrays(GL_TRIANGLE_FAN, 0, vertex_count)
