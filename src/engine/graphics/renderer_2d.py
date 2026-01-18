
from OpenGL.GL import *  # type: ignore
import numpy as np
from engine.graphics.opengl_3d_utils import MeshData, OpenGL_3D_Utils
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
        glBindVertexArray(0)

    def draw_texture(
        self,
        position: tuple[float, float],
        vao: int,
        shader,
        uPlayerPos: int,
        uIsPlayer: int,
        uUseTexture: int,
        uTexture: int,
        texture,
        uColor: int
    ) -> None:

        glUseProgram(shader)

        if uPlayerPos != -1 and position is not None:
            glUniform2f(uPlayerPos, float(position[0]), float(position[1]))

        if uIsPlayer != -1:
            glUniform1i(uIsPlayer, 1)

        if uUseTexture != -1:
            glUniform1i(uUseTexture, 1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        if uTexture != -1:
            glUniform1i(uTexture, 0)

        # Устанавливаем цвет в белый (чтобы текстура отображалась без изменения)
        if uColor != -1:
            glUniform4f(uColor, 1.0, 1.0, 1.0, 1.0)

        # Отрисовка
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glUseProgram(0)

    def create_vao_ebo(self, model_mesh: MeshData):
        vao = glGenVertexArrays(1)
        vbo_pos = glGenBuffers(1)
        vbo_norm = glGenBuffers(1)
        ebo_faces = glGenBuffers(1)
        ebo_edges = glGenBuffers(1)

        glBindVertexArray(vao)

        # Positions
        glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
        glBufferData(GL_ARRAY_BUFFER, model_mesh.vertices.nbytes, model_mesh.vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        # Normals
        glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
        glBufferData(GL_ARRAY_BUFFER, model_mesh.normals.nbytes, model_mesh.normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # Faces EBO
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, model_mesh.faces.nbytes, model_mesh.faces, GL_STATIC_DRAW)

        glBindVertexArray(0)

        # Edges EBO (можно биндать по необходимости)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_edges)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, model_mesh.edges.nbytes, model_mesh.edges, GL_STATIC_DRAW)

        return vao, ebo_faces, ebo_edges

    def draw_3d_model(
        self,
        position: tuple[float, float],
        size: tuple[float, float, float],
        color: tuple[float, float, float],
        vao: int,
        ebo_faces: int,
        shader,
        model_mesh: MeshData,
        projection: 'np.ndarray',
        view: 'np.ndarray',
        t: float,
        light_pos: 'np.ndarray',
        camera_pos: 'np.ndarray'
    ) -> None:

        model = OpenGL_3D_Utils.rotate(t)
        translate = OpenGL_3D_Utils.translate(position[0], position[1], 0.0)
        scale_mat = OpenGL_3D_Utils.scale(size[0], size[1], size[2])
        # Order: projection @ view @ translate(world) @ scale(local) @ rotate(local)
        mvp = projection @ view @ translate @ scale_mat @ model

        glUniformMatrix4fv(glGetUniformLocation(shader, "mvp"), 1, GL_TRUE, mvp)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model)
        glUniform3fv(glGetUniformLocation(shader, "lightPos"), 1, light_pos)
        glUniform3fv(glGetUniformLocation(shader, "viewPos"), 1, camera_pos)

        glBindVertexArray(vao)

        # --- Draw faces (opaque) ---
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        glUniform3f(glGetUniformLocation(shader, "objectColor"), *color)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
        glDrawElements(GL_TRIANGLES, len(model_mesh.faces), GL_UNSIGNED_INT, None)

        glDisable(GL_POLYGON_OFFSET_FILL)
        glEnable(GL_BLEND)
