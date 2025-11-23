import time
import pygame

pygame.init()
pygame.joystick.init()

for i in range(pygame.joystick.get_count()):
    j = pygame.joystick.Joystick(i)
    j.init()

while True:
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        print(id(j), j, j.get_guid())

    print('')
    print('')
    time.sleep(3)
