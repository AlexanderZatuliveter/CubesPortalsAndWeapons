import sys
import pygame
from pygame.event import Event

from game.consts import BLOCK_SIZE, MENU_FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH
from game.enums.window_enum import WindowEnum
from menus.base_menu import BaseMenu


class MapMenu(BaseMenu):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.map_path = "platform.map"
        self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2)

        buttons = {
            "Climbing": self.__make_map_callback("climbing.map"),
            "Just-face": self.__make_map_callback("just-face.map"),
            "Moon-or-not-moon": self.__make_map_callback("moon-or-not-moon.map"),
            "Pillars": self.__make_map_callback("pillars.map"),
            "Platform": self.__make_map_callback("platform.map"),
            "Sight": self.__make_map_callback("sight.map")
        }

        self._buttons = self._create_buttons(buttons)

    def show(self) -> None:
        self._joysticks_manager.current_first_button(self._buttons)
        
        self._running = True

        while self._running:
            events = pygame.event.get()

            self._update_common_events(events)
            for event in events:
                self._update_custom_events(event)
            self._joysticks_manager.update_joystick_selection(events, self._buttons)

            for button in self._buttons:
                button.update()

            self._draw_base()

            pygame.display.flip()
            self._clock.tick(MENU_FPS)

    def _update_custom_events(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def __make_map_callback(self, map_path):
        def callback():
            self.map_path = map_path
            self._game_state.current_window = WindowEnum.GAME_WINDOW

            if map_path == "climbing.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2)
            elif map_path == "moon-or-not-moon.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT - BLOCK_SIZE * 3)
            elif map_path == "just-face.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2 + BLOCK_SIZE * 4)
            elif map_path == "platform.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2)
            elif map_path == "pillars.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT / 2 - BLOCK_SIZE * 9)
            elif map_path == "sight.map":
                self.player_start_pos = (GAME_FIELD_WIDTH / 2, GAME_FIELD_HEIGHT - BLOCK_SIZE * 5)

            self._running = False
        return callback
