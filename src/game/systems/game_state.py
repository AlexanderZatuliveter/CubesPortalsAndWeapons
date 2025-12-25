
from game.enums.window_enum import WindowEnum


class GameState:
    def __init__(self):
        self.current_window: WindowEnum = WindowEnum.MAIN_MENU
