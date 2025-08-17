from OpenGL.GL import *  # type: ignore


class Renderer:
    def __init__(self):
        self.__quad_vertices: list[list[tuple[float, float]]] = []
        self.__quad_colors: list[tuple[float, float, float]] = []

        self.__line_vertices: list[list[tuple[float, float]]] = []
        self.__line_colors: list[tuple[float, float, float]] = []

        self.__tex_quads: list[tuple[int, list[tuple[float, float]], list[tuple[float, float]]]] = []
        # store: (texture_id, [coords], [texcoords])

    def add_quad(self, x: float, y: float, size: float, color: tuple[float, float, float]) -> None:
        self.__quad_vertices.append([
            (x, y),
            (x + size, y),
            (x + size, y + size),
            (x, y + size),
        ])
        self.__quad_colors.append(color)

    def add_outline(self, x: float, y: float, size: float, color: tuple[float, float, float]) -> None:
        self.__line_vertices.append([
            (x, y),
            (x + size, y),
            (x + size, y + size),
            (x, y + size),
        ])
        self.__line_colors.append(color)

    def add_texture_quad(self, texid: int, x: float, y: float, w: float, h: float) -> None:
        """Добавить текстурированный квадрат"""
        verts = [
            (x, y),
            (x + w, y),
            (x + w, y + h),
            (x, y + h),
        ]
        texcoords = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ]
        self.__tex_quads.append((texid, verts, texcoords))

    def render_all(self) -> None:
        """Отрисовать все накопленные примитивы"""

        # === QUADS ===
        glBegin(GL_QUADS)
        for verts, color in zip(self.__quad_vertices, self.__quad_colors):
            glColor3f(*color)
            for vx, vy in verts:
                glVertex2f(vx, vy)
        glEnd()

        # === OUTLINES ===
        for verts, color in zip(self.__line_vertices, self.__line_colors):
            glColor3f(*color)
            glBegin(GL_LINE_LOOP)
            for vx, vy in verts:
                glVertex2f(vx, vy)
            glEnd()

        # === TEXTURED QUADS ===
        glEnable(GL_TEXTURE_2D)
        for texid, verts, texcoords in self.__tex_quads:
            glBindTexture(GL_TEXTURE_2D, texid)
            glBegin(GL_QUADS)
            for (vx, vy), (tx, ty) in zip(verts, texcoords):
                glTexCoord2f(tx, ty)
                glVertex2f(vx, vy)
            glEnd()
        glDisable(GL_TEXTURE_2D)

        # Cleanup
        self.__quad_vertices.clear()
        self.__quad_colors.clear()
        self.__line_vertices.clear()
        self.__line_colors.clear()
        self.__tex_quads.clear()
