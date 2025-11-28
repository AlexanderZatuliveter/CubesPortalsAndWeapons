
import pygame


class MusicManager:
    def __init__(self) -> None:
        self.__music_file = "./music/dynamic_game_theme.mp3"

    def set_music(self, path: str) -> None:
        self.__music_file = path

    def set_volume(self, volume: float) -> None:
        pygame.mixer.music.set_volume(volume)

    def play(self) -> None:
        pygame.mixer.music.load(self.__music_file)
        pygame.mixer.music.play(-1)

    def stop(self) -> None:
        pygame.mixer.music.stop()

    def play_game_theme(self) -> None:
        self.set_music("./music/dynamic_game_theme.mp3")
        self.set_volume(0.6)
        self.play()

    def play_pause_music(self) -> None:
        self.set_music("./music/pause_menu_music.mp3")
        self.play()

    def play_main_menu_music(self) -> None:
        self.set_music("./music/main_menu_music.mp3")
        self.play()
