

import math
import os

import numpy as np
import trimesh

from dataclasses import dataclass
import numpy as np


@dataclass
class MeshData:
    vertices: np.ndarray  # (N, 3) float32
    normals: np.ndarray   # (N, 3) float32
    faces: np.ndarray     # (M,) uint32 (flat index buffer)
    edges: np.ndarray     # (K,) uint32 (flat index buffer)

    @property
    def face_count(self):
        return len(self.faces) // 3

    @property
    def vertex_count(self):
        return len(self.vertices)


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
    def load(file_path: str) -> MeshData:
        print(f"Загрузка модели: {file_path}...")

        if not os.path.exists(file_path):
            print(f"Файл {file_path} не найден! Генерируем тестовый тор.")
            mesh = trimesh.creation.torus(major_radius=0.5, minor_radius=0.2)
        else:
            mesh = trimesh.load(file_path)

        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)

        # === ТРАНСФОРМАЦИЯ ===
        angle_x = np.pi / 2
        rot_x = trimesh.transformations.rotation_matrix(angle_x, [1, 0, 0])
        angle_y = np.pi / 2
        rot_y = trimesh.transformations.rotation_matrix(angle_y, [0, 1, 0])
        full_transform = trimesh.transformations.concatenate_matrices(rot_y, rot_x)

        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError(f"Unsupported mesh type {type(mesh)}.")

        mesh.apply_transform(full_transform)
        mesh.vertices -= mesh.center_mass

        max_scale = np.max(mesh.extents)
        if max_scale > 0:
            mesh.vertices /= max_scale

        # Создаем экземпляр нашего нового класса
        data = MeshData(
            vertices=mesh.vertices.astype(np.float32),
            normals=mesh.vertex_normals.astype(np.float32),
            faces=mesh.faces.flatten().astype(np.uint32),
            edges=mesh.edges_unique.flatten().astype(np.uint32)
        )

        print(f"Модель загружена: {data.vertex_count} вершин, {data.face_count} граней.")
        return data
