import sys
import pygame
from pygame.event import Event

from engine.common import get_resource_path
from game.consts import BLUE, BUTTON_HEIGHT, MENU_FPS, GAME_FIELD_HEIGHT, GAME_FIELD_WIDTH, GREEN, ORANGE, RED, VICTORY_TEXT_HEIGHT, VICTORY_TEXT_WIDTH
from engine.ui.text_worker import TextWorker
from game.enums.window_enum import WindowEnum
from menus.base_menu import BaseMenu


class VictoryMenu(BaseMenu):
    def __init__(self, winner_color: tuple[float, float, float, float], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        def desktop_exit_button_func() -> None:
            pygame.quit()
            sys.exit()

        def restart_button_func() -> None:
            self._game_state.current_window = WindowEnum.GAME_WINDOW
            self._running = False

        def main_menu_button_func() -> None:
            self._game_state.current_window = WindowEnum.MAIN_MENU
            self._running = False

        buttons = {
            "Restart": restart_button_func,
            "Exit to Main Menu": main_menu_button_func,
            "Exit to Desktop": desktop_exit_button_func
        }

        self._buttons = self._create_buttons(buttons)

        self._text_rect = pygame.rect.Rect(
            GAME_FIELD_WIDTH / 2 - VICTORY_TEXT_WIDTH * 0.5,
            GAME_FIELD_HEIGHT / 3.5 - VICTORY_TEXT_HEIGHT * 0.5,
            VICTORY_TEXT_WIDTH,
            VICTORY_TEXT_HEIGHT
        )

        for consts_color in [BLUE, RED, GREEN, ORANGE]:
            if consts_color == winner_color:
                for name, value in globals().items():
                    if value is consts_color:
                        self._text = f"{name} PLAYER WIN"

        self._text_worker = TextWorker(
            x=self._text_rect.x,
            y=self._text_rect.y + BUTTON_HEIGHT * 0.25,
            text=self._text,
            rect_size=(self._text_rect.width, self._text_rect.height * 0.5),
            font=None,
            font_file_path=get_resource_path("src/_content/fonts/Orbitron-VariableFont_wght.ttf"),
            shader=self._shader,
            color=winner_color
        )

    def show(self) -> None:
        self._music_manager.play_victory_menu_music()
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

            # Draws
            self._draw_base()

            self._text_worker.draw()

            pygame.display.flip()
            self._clock.tick(MENU_FPS)

    def _update_custom_events(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._game_state.current_window = WindowEnum.GAME_WINDOW
                self._running = False
