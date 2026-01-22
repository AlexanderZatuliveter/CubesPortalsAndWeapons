
from typing import Literal
import pygame


class MusicManager:
    def __init__(self) -> None:
        self.__main_menu_music = "src/_content/music/main_menu_music.mp3"
        self.__pause_menu_music = "src/_content/music/pause_menu_music.mp3"
        self.__game_window_music = "src/_content/music/dynamic_game_theme.mp3"
        self.__victory_menu_music = "src/_content/music/victory_menu_music.mp3"

    def set_volume(self, volume: float) -> None:
        pygame.mixer.music.set_volume(volume)

    def play(self, path: str) -> None:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)

    def stop(self) -> None:
        pygame.mixer.music.stop()

    def play_game_theme(self) -> None:
        self.set_volume(0.6)
        self.play(self.__game_window_music)

    def play_pause_menu_music(self) -> None:
        self.set_volume(1.0)
        self.play(self.__pause_menu_music)

    def play_main_menu_music(self) -> None:
        self.set_volume(1.0)
        self.play(self.__main_menu_music)

    def play_victory_menu_music(self) -> None:
        self.set_volume(1.0)
        self.play(self.__victory_menu_music)
