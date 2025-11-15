import pygame
pygame.init()
pygame.joystick.init()

# словарь активных джойстиков
joysticks = {}

print("Ожидание событий... Подключайте/отключайте джойстики.")

running = True
while running:
    for event in pygame.event.get():

        # --- ПОДКЛЮЧЕНИЕ ---
        if event.type == pygame.JOYDEVICEADDED:
            # jid = event.which
            # js = pygame.joystick.Joystick(jid)
            # js.init()
            # joysticks[jid] = js

            print("\n=== JOYSTICK ADDED ===")
            print(f"jid: {event}")
            # print(f"name: {js.get_name()}")
            # print(f"Текущие джойстики: {list(joysticks.keys())}")

        # --- ОТКЛЮЧЕНИЕ ---
        if event.type == pygame.JOYDEVICEREMOVED:
            
            # jid = event.which
            # if jid in joysticks:
            #     del joysticks[jid]

            print("\n=== JOYSTICK REMOVED ===")
            print(f"jid: {event}")
            #print(f"Текущие джойстики: {list(joysticks.keys())}")

        # выход по ESC или крестик окна
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
