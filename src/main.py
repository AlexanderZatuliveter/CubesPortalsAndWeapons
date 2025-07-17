import pygame
import ctypes
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from consts import GAME_FIELD_PROPORTIONS, START_SCREEN_HEIGHT, START_SCREEN_WIDTH
from main_window import MainWindow


# Set process DPI awareness. Use 1 for "System DPI Awareness", or 2 for "Per-Monitor DPI Awareness"
ctypes.windll.shcore.SetProcessDpiAwareness(1)

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=100)

info = pygame.display.Info()

target_width = info.current_w * 0.8
target_height = target_width / GAME_FIELD_PROPORTIONS
screen_size = (START_SCREEN_WIDTH, START_SCREEN_HEIGHT)

screen = pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL | RESIZABLE)
pygame.display.set_caption("Cubes, portals & weapons")

clock = pygame.time.Clock()

main_window = MainWindow(screen, clock)
main_window.show()
