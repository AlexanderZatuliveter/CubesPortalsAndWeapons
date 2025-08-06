import pygame
import sys
import math

# Инициализация
pygame.init()
pygame.joystick.init()

# Проверка наличия контроллера
if pygame.joystick.get_count() == 0:
    print("Контроллер не найден.")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Куб + Контроллер Xbox 360")

# Куб
cube_size = 100
x, y = WIDTH // 2, HEIGHT // 2
speed = 5
angle = 0  # Угол поворота куба

clock = pygame.time.Clock()

# Функция отрисовки повернутого куба
def draw_rotated_cube(surface, color, center, size, angle):
    half = size // 2
    points = [
        (-half, -half),
        (half, -half),
        (half, half),
        (-half, half),
    ]

    # Вращение точек
    rotated_points = []
    for px, py in points:
        rx = px * math.cos(angle) - py * math.sin(angle)
        ry = px * math.sin(angle) + py * math.cos(angle)
        rotated_points.append((center[0] + rx, center[1] + ry))

    pygame.draw.polygon(surface, color, rotated_points)

# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Управление стиками
    axis_x = joystick.get_axis(0)  # Левый стик X
    axis_y = joystick.get_axis(1)  # Левый стик Y
    axis_rx = joystick.get_axis(3)  # Правый стик X
    axis_ry = joystick.get_axis(4)  # Правый стик Y

    # Dead zone
    dead_zone = 0.1
    if abs(axis_x) < dead_zone:
        axis_x = 0
    if abs(axis_y) < dead_zone:
        axis_y = 0
    if abs(axis_rx) < dead_zone:
        axis_rx = 0
    if abs(axis_ry) < dead_zone:
        axis_ry = 0

    # Движение от стиков
    x += axis_x * speed
    y += axis_y * speed

    # Управление кнопками
    if joystick.get_button(0):  # A
        y += speed
    if joystick.get_button(1):  # B
        x += speed
    if joystick.get_button(2):  # X
        x -= speed
    if joystick.get_button(3):  # Y
        y -= speed

    # Вращение от правого стика
    angle += axis_rx * 0.05  # чувствительность поворота

    # Ограничения по краям экрана
    x = max(cube_size // 2, min(WIDTH - cube_size // 2, x))
    y = max(cube_size // 2, min(HEIGHT - cube_size // 2, y))

    # Отрисовка
    screen.fill((30, 30, 30))
    draw_rotated_cube(screen, (0, 200, 255), (x, y), cube_size, angle)
    pygame.display.flip()
    clock.tick(60)
