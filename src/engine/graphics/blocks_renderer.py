"""
Optimized batch renderer for static blocks using instanced rendering.
Reduces draw calls from 2000+ to 1.
"""

from OpenGL.GL import *  # type: ignore
import numpy as np
import ctypes

from game.consts import BLOCK_SIZE, DARK_GREY
from engine.graphics.opengl_utils import OpenGLUtils


class BlocksRenderer:
    """Renders all blocks in a single draw call using instanced rendering."""

    def __init__(self, shader):
        """
        Initialize the block renderer.

        Args:
            shader: The 2D shader program to use for rendering
        """
        self.__shader = shader
        self.__vao = None
        self.__vbo_positions = None
        self.__vbo_vertices = None
        self.__vertex_count = 4
        self.__instance_count = 0

        # Cache uniform locations
        self.__uUseTexture = glGetUniformLocation(shader, "uUseTexture")
        self.__uIsPlayer = glGetUniformLocation(shader, "uIsPlayer")
        self.__uColor = glGetUniformLocation(shader, "uColor")

        self.__setup_vao()

    def __setup_vao(self):
        """Setup VAO with vertex and instance position data."""
        # Create VAO
        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)

        # Vertex position data (single square)
        vertices = OpenGLUtils.create_square_vertices(BLOCK_SIZE)
        self.__vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Vertex position attribute (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

        # Instance position buffer (will be updated each frame)
        self.__vbo_positions = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.__vbo_positions)
        # Allocate empty buffer (will be updated in draw())
        glBufferData(GL_ARRAY_BUFFER, 0, None, GL_DYNAMIC_DRAW)

        # Instance position attribute (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
        glVertexAttribDivisor(1, 1)  # Advance once per instance

        glBindVertexArray(0)

    def draw(self, positions: list[tuple[float, float]]) -> None:
        """
        Draw all blocks at specified positions.

        Args:
            positions: List of (x, y) positions for blocks
        """
        if not positions:
            return

        # Update instance position buffer
        positions_array = np.array(positions, dtype=np.float32)

        glBindBuffer(GL_COPY_WRITE_BUFFER, self.__vbo_positions)
        glBufferData(
            GL_COPY_WRITE_BUFFER,
            positions_array.nbytes,
            positions_array,
            GL_DYNAMIC_DRAW
        )

        # Setup shader
        glUseProgram(self.__shader)
        glUniform1i(self.__uUseTexture, 0)  # No texture for blocks
        glUniform1i(self.__uIsPlayer, 0)    # Not player
        glUniform4f(self.__uColor, *DARK_GREY)

        # Draw all instances in one call
        glBindVertexArray(self.__vao)
        glDrawArraysInstanced(GL_TRIANGLE_FAN, 0, self.__vertex_count, len(positions))
        glBindVertexArray(0)

    def cleanup(self) -> None:
        """Free GPU resources."""
        if self.__vao:
            glDeleteBuffers(1, [self.__vbo_vertices])
            glDeleteBuffers(1, [self.__vbo_positions])
            glDeleteVertexArrays(1, [self.__vao])
            self.__vao = None
            self.__vbo_vertices = None
            self.__vbo_positions = None
