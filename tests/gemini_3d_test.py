# pip install pyopengl pyopengl_accelerate glfw numpy trimesh

import glfw
from OpenGL.GL import *  # type: ignore
import numpy as np
import math
import time
import trimesh  # Добавлена библиотека для загрузки моделей
import os

# ================== SHADERS ==================

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
uniform mat4 mvp;
void main()
{
    gl_Position = mvp * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
uniform vec4 color;
void main()
{
    FragColor = color;
}
"""

# ================== HELPERS ==================


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader


def create_program(vs, fs):
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program))
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program


def ortho(left, right, bottom, top, near, far):
    return np.array([
        [2 / (right - left), 0, 0, -(right + left) / (right - left)],
        [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
        [0, 0, -2 / (far - near), -(far + near) / (far - near)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def look_at(eye, target, up):
    f = normalize(target - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)

    return np.array([
        [s[0], u[0], -f[0], -np.dot(s, eye)],
        [s[1], u[1], -f[1], -np.dot(u, eye)],
        [s[2], u[2], -f[2], np.dot(f, eye)],
        [0, 0, 0, 1]
    ], dtype=np.float32)

# Вращение вокруг оси Y


def rotate(angle):
    return rotate_y(90)

# Вращение вокруг оси X (как сальто)


def rotate_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

# Вращение вокруг оси Y (как юла)


def rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, 0, s, 0],  # X
        [0, 1, 0, 0],  # Y
        [-s, 0, c, 0],  # Z
        [0, 0, 0, 1]
    ], dtype=np.float32)

# Вращение вокруг оси Z (как пропеллер)


def rotate_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

# НОВОЕ: Функция загрузки и подготовки модели


def load_and_normalize_mesh(file_path):
    print(f"Загрузка модели: {file_path}...")

    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден! Генерируем тестовый тор.")
        mesh = trimesh.creation.torus(major_radius=0.5, minor_radius=0.2)
    else:
        mesh = trimesh.load(file_path)

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)

    # === ИСПРАВЛЕНИЕ ОРИЕНТАЦИИ ===
    # Поворачиваем модель на -90 градусов вокруг оси X.
    # Это превращает "Z-вверх" (CAD) в "Y-вверх" (OpenGL)

    # Создаем матрицу поворота вручную
    angle = -np.pi / 2  # -90 градусов
    c = np.cos(angle)
    s = np.sin(angle)
    rotation_matrix = np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ])

    # Применяем поворот к самому мешу
    mesh.apply_transform(rotation_matrix)
    # ==============================

    # 1. Центрируем модель ПОСЛЕ поворота
    if isinstance(mesh, trimesh.Trimesh):
        mesh.vertices -= mesh.center_mass

        # 2. Масштабируем
        max_scale = np.max(mesh.extents)
        if max_scale > 0:
            mesh.vertices /= max_scale

        vertices = mesh.vertices.flatten().astype(np.float32)
        faces = mesh.faces.flatten().astype(np.uint32)
        edges = mesh.edges_unique.flatten().astype(np.uint32)

    print(f"Модель загружена: {len(vertices) // 3} вершин, {len(faces) // 3} граней.")
    return vertices, faces, edges


# ================== MAIN ==================


def main():
    # === НАСТРОЙКИ ===
    # Укажите путь к вашему файлу (.obj, .stl, .ply, .glb)
    # MODEL_PATH = "tests/.wheel.STL"
    MODEL_PATH = "src/_content/3D_models/laser_gun.STL"
    # =================

    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    width, height = 1000, 800
    window = glfw.create_window(width, height, "3D Model Viewer", None, None)
    glfw.make_context_current(window)

    vertices, face_indices, edge_indices = load_and_normalize_mesh(MODEL_PATH)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo_faces = glGenBuffers(1)
    ebo_edges = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, face_indices.nbytes, face_indices, GL_STATIC_DRAW)

    glBindVertexArray(0)

    # Буфер для ребер (сетки)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_edges)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, edge_indices.nbytes, edge_indices, GL_STATIC_DRAW)

    program = create_program(
        compile_shader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compile_shader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    glEnable(GL_DEPTH_TEST)
    # Включаем сглаживание линий, чтобы сетка выглядела приятнее
    glEnable(GL_LINE_SMOOTH)

    start = time.time()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Задает цвет фона (например, черный или темно-серый)
        glClearColor(0.1, 0.1, 0.12, 1)
        # Очищает буфер цвета (картинку) и буфер глубины (Z-буфер)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        t = time.time() - start

        # Обновляем aspect ratio на случай изменения размера окна
        w, h = glfw.get_framebuffer_size(window)
        if h == 0:
            h = 1  # защита от деления на 0
        glViewport(0, 0, w, h)

        aspect_ratio = w / h
        ortho_height = 2.5  # Немного увеличим обзор
        ortho_width = ortho_height * aspect_ratio

        projection = ortho(-ortho_width / 2, ortho_width / 2, -ortho_height / 2, ortho_height / 2, -10, 10)

        view = look_at(
            np.array([0.0, 0.0, 2.5], dtype=np.float32),  # Позиция камеры
            np.array([0.0, 0.0, 0.0], dtype=np.float32),  # Куда смотрит (в центр)
            np.array([0.0, 1.0, 0.0], dtype=np.float32)  # Где "верх" (ось Y)
        )

        # Вращение вокруг одной оси (Y)
        model = rotate(t)

        mvp = projection @ view @ model

        glUseProgram(program)
        glUniformMatrix4fv(glGetUniformLocation(program, "mvp"), 1, GL_TRUE, mvp)

        glBindVertexArray(vao)

        # 1. Рисуем грани (тело объекта)
        # Цвет: голубоватый
        glUniform4f(glGetUniformLocation(program, "color"), 0.2, 0.5, 0.8, 1.0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
        glDrawElements(GL_TRIANGLES, len(face_indices), GL_UNSIGNED_INT, None)

        # 2. Рисуем ребра (сетку) поверх
        # Цвет: черный или белый (для контраста)
        glUniform4f(glGetUniformLocation(program, "color"), 1.0, 1.0, 1.0, 0.4)  # Белый полупрозрачный
        glLineWidth(1.0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_edges)
        glDrawElements(GL_LINES, len(edge_indices), GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
