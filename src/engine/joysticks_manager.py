

import pygame
from pygame.event import Event

from engine.ui.button import Button
from game.enums.direction_enum import DirectionEnum


class JoysticksManager:

    def __init__(self):
        self.__current_button_i = 0
        self.__joysticks = self.get_joysticks()

    def get_joysticks(self) -> list[pygame.joystick.JoystickType]:
        joysticks: list = []
        for num in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(num)
            if 'Receiver' in joystick.get_name():
                continue
            joystick.init()
            joysticks.append(joystick)
        return joysticks

    def update_joystick_selection(self, events: list[Event], buttons: list[Button]):
        for event in events:

            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:
                    axis_y = event.value
                    dead_zone = 0.5
                    if axis_y < -dead_zone:
                        if self.__axis_dir != -1:
                            self.__joystick_move_selection(DirectionEnum.UP, buttons)
                            self.__axis_dir = -1
                    elif axis_y > dead_zone:
                        if self.__axis_dir != 1:
                            self.__joystick_move_selection(DirectionEnum.DOWN, buttons)
                            self.__axis_dir = 1
                    else:
                        if abs(axis_y) < dead_zone:
                            self.__axis_dir = 0

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    for button in buttons:
                        if button.is_current():
                            button.set_active()

    def __joystick_move_selection(self, direction: DirectionEnum, buttons: list[Button]) -> None:
        if direction == DirectionEnum.DOWN:
            dir_num = 1
        else:
            dir_num = -1

        count = len(buttons)
        buttons[self.__current_button_i].unset_current_button()
        self.__current_button_i = (self.__current_button_i + dir_num) % count
        buttons[self.__current_button_i].set_current_button()
