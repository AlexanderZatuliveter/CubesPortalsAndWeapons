import pygame

pygame.init()

# Настройки окна
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Variable Jump Height Demo")
clock = pygame.time.Clock()

# Куб
cube_size = 40
x = WIDTH // 2 - cube_size // 2
y = HEIGHT - cube_size
velocity_y = 0

# Флаги состояния
on_ground = True
jumping = False

# Параметры физики
gravity = 0.5         # обычная гравитация
low_gravity = 0.2     # гравитация при удержании кнопки
jump_force = -10      # сила начала прыжка
max_fall_speed = 10   # ограничение падения

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Начало прыжка
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a and on_ground:
            velocity_y = jump_force
            on_ground = False
            jumping = True

        # Отпустили кнопку — убираем эффект “удержания”
        if event.type == pygame.KEYUP and event.key == pygame.K_a:
            jumping = False

    keys = pygame.key.get_pressed()

    # Меньшая гравитация при удержании кнопки во время подъёма
    if jumping and keys[pygame.K_a] and velocity_y < 0:
        velocity_y += low_gravity
    else:
        velocity_y += gravity

    # Ограничение падения
    if velocity_y > max_fall_speed:
        velocity_y = max_fall_speed

    # Обновляем позицию куба
    y += velocity_y

    # Проверка земли
    if y >= HEIGHT - cube_size:
        y = HEIGHT - cube_size
        velocity_y = 0
        on_ground = True
        jumping = False

    # Рендер
    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 200, 255), (x, y, cube_size, cube_size))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
