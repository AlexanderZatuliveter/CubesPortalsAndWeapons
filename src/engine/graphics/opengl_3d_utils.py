

import math
import os

import numpy as np
import trimesh


class OpenGL_3D_Utils:

    @staticmethod
    def rotate(angle):
        c = math.cos(angle)
        s = math.sin(angle)
        return np.array([
            [c, 0, s, 0],  # X
            [0, 1, 0, 0],  # Y
            [-s, 0, c, 0],  # Z
            [0, 0, 0, 1]
        ], dtype=np.float32)

    @staticmethod
    def translate(x: float, y: float, z: float):
        """Create a 4x4 translation matrix (row-major)"""
        return np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1],
        ], dtype=np.float32)

    @staticmethod
    def scale(sx: float, sy: float, sz: float):
        """Create a 4x4 scale matrix (row-major)"""
        return np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ], dtype=np.float32)

    @staticmethod
    def load_and_normalize_mesh(file_path):
        print(f"Загрузка модели: {file_path}...")

        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден! Генерируем тестовый тор.")
            mesh = trimesh.creation.torus(major_radius=0.5, minor_radius=0.2)
        else:
            mesh = trimesh.load(file_path)

        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)

        # === ИСПРАВЛЕНИЕ ОРИЕНТАЦИИ (X-90 и Y+90) ===

        # 1. Поворот по X на -90 градусов (исправляет вертикальное положение)
        angle_x = np.pi / 2
        rot_x = trimesh.transformations.rotation_matrix(angle_x, [1, 0, 0])

        # 2. Поворот по Y на 90 градусов (ваш запрос)
        angle_y = np.pi / 2
        rot_y = trimesh.transformations.rotation_matrix(angle_y, [0, 1, 0])

        # Объединяем трансформации (порядок: сначала X, потом Y)
        full_transform = trimesh.transformations.concatenate_matrices(rot_y, rot_x)

        if isinstance(mesh, trimesh.Trimesh):
            # Применяем к мешу
            mesh.apply_transform(full_transform)
            # ===========================================

            # Центрируем модель после всех поворотов
            mesh.vertices -= mesh.center_mass

            # Масштабируем до единичного размера
            max_scale = np.max(mesh.extents)
            if max_scale > 0:
                mesh.vertices /= max_scale

            # Возвращаем массивы в форме (N, 3) для удобства работы с VBO
            vertices = mesh.vertices.astype(np.float32)
            # Генерируем нормали для вершин (trimesh предоставляет vertex_normals)
            normals = mesh.vertex_normals.astype(np.float32)
            faces = mesh.faces.flatten().astype(np.uint32)
            edges = mesh.edges_unique.flatten().astype(np.uint32)

        print(f"Модель загружена: {len(vertices)} вершин, {len(faces) // 3} граней.")
        return vertices, normals, faces, edges
