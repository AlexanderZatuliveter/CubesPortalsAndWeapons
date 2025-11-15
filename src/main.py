import pygame
import ctypes
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from consts import SCREEN_HEIGHT, SCREEN_WIDTH
from main_window import MainWindow


# Set process DPI awareness. Use 1 for "System DPI Awareness", or 2 for "Per-Monitor DPI Awareness"
ctypes.windll.shcore.SetProcessDpiAwareness(1)

pygame.init()
pygame.joystick.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
pygame.display.set_caption("Cubes, portals & weapons")

clock = pygame.time.Clock()

main_window = MainWindow(screen, clock)
main_window.show()
