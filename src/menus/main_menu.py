import sys
import pygame
from pygame.event import Event

from game.consts import MENU_FPS
from game.enums.window_enum import WindowEnum
from menus.base_menu import BaseMenu


class MainMenu(BaseMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def desktop_exit_button_func() -> None:
            pygame.quit()
            sys.exit()

        def start_button_func() -> None:
            self._game_state.current_window = WindowEnum.MAP_MENU
            self._running = False

        buttons = {
            "Start": start_button_func,
            "Exit to Desktop": desktop_exit_button_func
        }

        self._buttons = self._create_buttons(buttons)

    def _update_custom_events(self, event: Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    def show(self):
        self._music_manager.play_main_menu_music()
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
