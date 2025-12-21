import pygame
import sys

pygame.init()
pygame.joystick.init()

# Чёрное окно
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Xbox 360 rumble test")

BLACK = (0, 0, 0)

# Проверяем, есть ли джойстик
if pygame.joystick.get_count() == 0:
    print("Геймпад не найден")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Подключен:", joystick.get_name())

clock = pygame.time.Clock()
rumbling = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Нажатие кнопки
        if event.type == pygame.JOYBUTTONDOWN:
            # Кнопка A у Xbox 360 обычно = 0
            if event.button == 0:
                # (low_freq, high_freq, duration_ms)
                joystick.rumble(1.0, 1.0, 0)
                rumbling = True

        # Отпускание кнопки
        if event.type == pygame.JOYBUTTONUP:
            if event.button == 0:
                joystick.stop_rumble()
                rumbling = False

    screen.fill(BLACK)
    pygame.display.flip()
    clock.tick(60)

joystick.stop_rumble()
pygame.quit()
