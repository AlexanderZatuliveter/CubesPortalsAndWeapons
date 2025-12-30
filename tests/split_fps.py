import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *  # type: ignore
import time

# =========================
# НАСТРОЙКИ FPS
# =========================
UPDATE_FPS = 300
DRAW_FPS = 120

UPDATE_DT = 1.0 / UPDATE_FPS
DRAW_DT = 1.0 / DRAW_FPS

# =========================
# INIT
# =========================
pygame.init()
pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Update 300 FPS | Draw 120 FPS")

glClearColor(0.1, 0.1, 0.1, 1)

# =========================
# ПЕРЕМЕННЫЕ ИГРЫ
# =========================
x = -0.5
speed = 0.5  # единиц в секунду


def update(dt):
    global x
    x += speed * dt
    if x > 1:
        x = -1


def draw():
    glClear(GL_COLOR_BUFFER_BIT)

    glBegin(GL_QUADS)
    glColor4f(0.2, 0.8, 0.3, 1.0)
    glVertex2f(x, -0.2)
    glVertex2f(x + 0.2, -0.2)
    glVertex2f(x + 0.2, 0.2)
    glVertex2f(x, 0.2)
    glEnd()

    pygame.display.flip()


# =========================
# ОСНОВНОЙ ЦИКЛ
# =========================
running = True

last_time = time.perf_counter()
update_accumulator = 0.0
draw_accumulator = 0.0

while running:
    now = time.perf_counter()
    frame_time = now - last_time
    last_time = now

    update_accumulator += frame_time
    draw_accumulator += frame_time

    # ---- EVENTS ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- UPDATE (300 FPS) ----
    while update_accumulator >= UPDATE_DT:
        update(UPDATE_DT)
        update_accumulator -= UPDATE_DT

    # ---- DRAW (120 FPS) ----
    if draw_accumulator >= DRAW_DT:
        draw()
        draw_accumulator = 0.0

pygame.quit()
