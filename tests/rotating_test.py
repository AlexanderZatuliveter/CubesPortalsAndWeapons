import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math

# Шейдеры (GLSL)
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 rotation;

void main() {
    gl_Position = rotation * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(0.0, 0.7, 1.0, 1.0); // Голубой цвет
}
"""


def create_rotation_matrix(angle_deg):
    """Создает матрицу поворота вокруг оси Z."""
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Матрица 4x4 (column-major order для OpenGL)
    return np.array([
        [cos_a, -sin_a, 0, 0],
        [sin_a, cos_a, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def main():
    pygame.init()
    pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Step Rotation 45°")

    # Компиляция шейдеров
    shader = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    # Вершины квадрата (2 треугольника)
    vertices = np.array([
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        0.5, 0.5, 0.0,

        -0.5, -0.5, 0.0,
        0.5, 0.5, 0.0,
        -0.5, 0.5, 0.0
    ], dtype=np.float32)

    # Создание VAO и VBO
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Указываем, как интерпретировать данные вершин
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glUseProgram(shader)
    rotation_loc = glGetUniformLocation(shader, "rotation")

    clock = pygame.time.Clock()
    angle = 0
    last_rotation_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Логика поворота: проверяем, прошла ли 1 секунда (1000 мс)
        current_time = pygame.time.get_ticks()
        if current_time - last_rotation_time >= 1000:
            angle += 45
            last_rotation_time = current_time

        # Очистка экрана
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Передача матрицы поворота в шейдер
        rot_matrix = create_rotation_matrix(angle)
        glUniformMatrix4fv(rotation_loc, 1, GL_FALSE, rot_matrix)

        # Отрисовка
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        pygame.display.flip()
        clock.tick(60)

    # Очистка ресурсов
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    pygame.quit()


if __name__ == "__main__":
    main()
