import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# позиция квадрата
player_x = 0
player_y = 0


def draw_square(x, y, size=0.1):
    glPushMatrix()
    glTranslatef(x, y, 0)

    glBegin(GL_QUADS)
    glVertex2f(-size, -size)
    glVertex2f(size, -size)
    glVertex2f(size, size)
    glVertex2f(-size, size)
    glEnd()

    glPopMatrix()


def main():
    global player_x, player_y

    pygame.init()
    pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL)

    # ортопроекция (2D)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)

    glMatrixMode(GL_MODELVIEW)

    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000   # секунды

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- управление
        keys = pygame.key.get_pressed()
        speed = 1.0

        if keys[pygame.K_LEFT]:
            player_x -= speed * dt
        if keys[pygame.K_RIGHT]:
            player_x += speed * dt
        if keys[pygame.K_UP]:
            player_y += speed * dt
        if keys[pygame.K_DOWN]:
            player_y -= speed * dt

        # --- отрисовка
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # рисуем игрока
        draw_square(player_x, player_y)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
