
from pygame.event import Event
import pygame

from game.entities.bullets import Bullets
from game.consts import BLUE, RED, GREEN, ORANGE
from game.game_field import GameField
from game.entities.player import Player


class Players(list[Player]):
    def __init__(
        self,
        game_field: GameField,
        shader,
        bullets: Bullets
    ) -> None:
        self.__colors = [BLUE, RED, GREEN, ORANGE]
        self.__bullets = bullets
        self.__shader = shader
        self.__game_field = game_field

    def update(self, events: list[Event]):
        self.__joystick_events(events)
        for player in self:
            player.update()

    def __joystick_events(self, events: list[Event]):
        self.__players_append()

        for event in events:
            if event.type == pygame.JOYDEVICEADDED:
                print("JOYDEVICEADDED")
                self.__players_append()

            # if event.type == pygame.JOYDEVICEREMOVED:
            #     print("JOYDEVICEREMOVED")
            #     self.__players[list(self.__players.keys())[0]] = 0
            #     print(f"{self.__players=}")

    def __get_joysticks(self) -> list[pygame.joystick.JoystickType]:
        joysticks: list = []
        for num in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(num)
            if 'Receiver' in joystick.get_name():
                continue
            joystick.init()
            joysticks.append(joystick)
        return joysticks

    def __players_append(self) -> None:
        joysticks = {id(j): j for j in self.__get_joysticks()}
        player_joysticks = {id(player.get_joystick()): player for player in self}

        # получить список неактивных игроков
        # найти не назначенные джойстики
        # назначить им не назначенные джойстики
        inactive_player_joystick_ids: set[int] = set(player_joysticks.keys()) - set(joysticks.keys())
        inactive_joystick_ids = set(joysticks.keys()) - set(player_joysticks.keys())
        for player_joystick_id in inactive_player_joystick_ids:
            if len(inactive_joystick_ids) > 0:
                joystick_id = inactive_joystick_ids.pop()
                player_joysticks[player_joystick_id].set_joystick(joysticks[joystick_id])

        for inactive_joystick_id in inactive_joystick_ids:
            new_player = Player(
                self.__game_field,
                self.__shader,
                self.__colors[len(self)],
                self.__bullets
            )
            new_player.set_joystick(joysticks[inactive_joystick_id])
            self.append(new_player)
