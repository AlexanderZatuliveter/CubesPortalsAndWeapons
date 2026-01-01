import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import ctypes

# --- Шейдеры (на языке GLSL) ---

vertex_src = """
#version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

out vec2 v_texture;

void main()
{
    gl_Position = vec4(a_position, 1.0);
    v_texture = a_texture;
}
"""

fragment_src = """
#version 330
in vec2 v_texture;
out vec4 out_color;

uniform sampler2D s_texture;

void main()
{
    out_color = texture(s_texture, v_texture);
}
"""


def load_texture(path):
    # 1. Загружаем изображение через Pygame
    image = pygame.image.load(path)

    # 2. Переворачиваем и преобразуем в байты
    # OpenGL считает (0,0) левым нижним углом, а Pygame - верхним левым.
    # Третий аргумент 'True' в tostring переворачивает картинку по вертикали.
    texture_data = pygame.image.tostring(image, "RGBA", True)

    width = image.get_width()
    height = image.get_height()

    # 3. Генерируем текстуру в OpenGL
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # 4. Настройки фильтрации и повторения
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # 5. Загружаем данные (байты) в GPU
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    return texture


def main():
    # Инициализация Pygame и OpenGL контекста
    pygame.init()
    pygame.display.set_mode((800, 600), OPENGL | DOUBLEBUF)
    pygame.display.set_caption("OpenGL Texture in Python")

    # Цвет очистки экрана
    glClearColor(0.1, 0.2, 0.2, 1)

    # Компиляция шейдеров
    shader = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER)
    )

    # --- Данные вершин (VAO/VBO) ---
    # Формат: X, Y, Z, U, V
    vertices = [
        # Позиции          # Текстурные коорд.
        -0.5, -0.5, 0.0, 0.0, 0.0,  # 0 левый нижний
        0.5, -0.5, 0.0, 1.0, 0.0,  # 1 правый нижний
        0.5, 0.5, 0.0, 1.0, 1.0,  # 2 правый верхний
        -0.5, 0.5, 0.0, 0.0, 1.0  # 3 левый верхний
    ]

    # Индексы для отрисовки двух треугольников, составляющих квадрат
    indices = [
        0, 1, 2,
        2, 3, 0
    ]

    # Конвертируем в numpy массивы (обязательно float32 для вершин!)
    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    # Создаем буферы
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    # Привязываем VAO
    glBindVertexArray(VAO)

    # VBO (данные вершин)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # EBO (индексы)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Настраиваем атрибуты (Stride и Offset)
    # Stride = размер одной строки данных в байтах (5 float * 4 байта = 20 байт)
    stride = vertices.itemsize * 5

    # Позиция (location = 0): 3 float, смещение 0
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    # Текстура (location = 1): 2 float, смещение 12 байт (3 float * 4 байта)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

    # Загружаем текстуру (укажите свой файл!)
    try:
        my_texture = load_texture("src/_content/images/laser_gun.png")
    except Exception as e:
        print(f"Ошибка загрузки текстуры: {e}")
        # Создадим пустую текстуру или завершим работу, если критично
        return

    glUseProgram(shader)

    # Главный цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT)

        # Рисуем
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, my_texture)

        glBindVertexArray(VAO)
        # 6 вершин (2 треугольника)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


if __name__ == "__main__":
    main()
