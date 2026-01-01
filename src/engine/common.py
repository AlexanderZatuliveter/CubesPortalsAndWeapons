import os
import sys
import pygame
from OpenGL.GL import *  # type: ignore


def get_screen_resolution() -> tuple[float, float]:
    ctypes.windll.user32.SetProcessDPIAware()
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    return width, height


def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS  # type: ignore
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_texture(path):
    # 1. Загружаем изображение через Pygame
    image = pygame.image.load(path)

    # ratio = image.get_width() / image.get_height(), image.get_height() / image.get_height()
    ratio = image.get_width() / image.get_width() * 2, image.get_height() / image.get_width() * 2

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

    return texture, ratio
