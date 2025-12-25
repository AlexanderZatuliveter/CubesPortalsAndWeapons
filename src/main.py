import pygame
import ctypes
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE

from game.consts import SCREEN_HEIGHT, SCREEN_WIDTH
from game.windows.main_menu import MainMenu
from game.windows.game_window import GameWindow
from engine.music_manager import MusicManager
from game.windows.pause_menu import PauseMenu
from game.systems.game_state import GameState
from game.windows.victory_menu import VictoryMenu
from game.enums.window_enum import WindowEnum


# Set process DPI awareness. Use 1 for "System DPI Awareness", or 2 for "Per-Monitor DPI Awareness"
ctypes.windll.shcore.SetProcessDpiAwareness(1)

pygame.init()
pygame.joystick.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE)
pygame.display.set_caption("Cubes, portals & weapons")

clock = pygame.time.Clock()

music_manager = MusicManager()

game_state = GameState()

main_menu = MainMenu(game_state, screen, clock, music_manager)
pause_menu = PauseMenu(game_state, screen, clock, music_manager)
game_window = GameWindow(game_state, screen, clock, music_manager)

while True:
    if game_state.current_window == WindowEnum.MAIN_MENU:
        main_menu.show()
        game_window = GameWindow(game_state, screen, clock, music_manager)

    elif game_state.current_window == WindowEnum.GAME_WINDOW:
        variable = game_window.show()
        if variable is not None:
            winner_color = variable

    elif game_state.current_window == WindowEnum.PAUSE_MENU:
        pause_menu.show()

    elif game_state.current_window == WindowEnum.VICTORY_MENU:
        victory_menu = VictoryMenu(winner_color, game_state, screen, clock, music_manager)
        victory_menu.show()
        game_window = GameWindow(game_state, screen, clock, music_manager)
