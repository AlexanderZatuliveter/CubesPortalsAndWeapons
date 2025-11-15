import pygame

pygame.init()
pygame.joystick.init()

print("Ожидание подключения джойстиков...")
print("Подключите джойстики по очереди, чтобы увидеть все данные события\n")

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYDEVICEADDED:
            print("=" * 50)
            print("JOYDEVICEADDED событие:")
            print(f"  event.device_index: {event.device_index}")

            # Все атрибуты события
            print(f"  Все атрибуты события: {dir(event)}")

            # Инициализируем джойстик чтобы получить больше информации
            joystick = pygame.joystick.Joystick(event.device_index)
            joystick.init()

            print(f"\nИнформация о джойстике:")
            print(f"  get_name(): {joystick.get_name()}")
            print(f"  get_guid(): {joystick.get_guid()}")
            print(f"  get_instance_id(): {joystick.get_instance_id()}")
            print(f"  get_id(): {joystick.get_id()}")
            print(f"  get_numaxes(): {joystick.get_numaxes()}")
            print(f"  get_numbuttons(): {joystick.get_numbuttons()}")
            print(f"  get_numhats(): {joystick.get_numhats()}")

            # Проверяем есть ли другие методы
            print(f"\n  Все методы джойстика:")
            for method in dir(joystick):
                if not method.startswith('_'):
                    print(f"    - {method}")

            print("=" * 50 + "\n")

        elif event.type == pygame.JOYDEVICEREMOVED:
            print(f"JOYDEVICEREMOVED: instance_id = {event.instance_id}\n")

    clock.tick(60)

pygame.quit()
