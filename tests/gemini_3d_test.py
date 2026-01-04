import glfw
from OpenGL.GL import *
import numpy as np
import math
import time
import trimesh
import os

# ================== SHADERS (Phong Lighting) ==================

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;

uniform mat4 model;
uniform mat4 mvp;

void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    // Нормали нужно трансформировать правильно (без учета масштабирования)
    Normal = mat3(transpose(inverse(model))) * aNormal;
    gl_Position = mvp * vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 objectColor;

void main()
{
    // 1. Ambient (фоновое освещение)
    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);

    // 2. Diffuse (рассеянный свет)
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0);

    // 3. Specular (Металлический блик)
    float specularStrength = 0.8; // Интенсивность блеска
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    // 32 - это коэффициент глянца (чем выше, тем меньше и резче блик)
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 64);
    vec3 specular = specularStrength * spec * vec3(1.0, 1.0, 1.0);

    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, 1.0);
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
    return program


def ortho(left, right, bottom, top, near, far):
    return np.array([
        [2 / (right - left), 0, 0, -(right + left) / (right - left)],
        [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
        [0, 0, -2 / (far - near), -(far + near) / (far - near)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def normalize_v(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def look_at(eye, target, up):
    f = normalize_v(target - eye)
    s = normalize_v(np.cross(f, up))
    u = np.cross(s, f)
    return np.array([
        [s[0], u[0], -f[0], -np.dot(s, eye)],
        [s[1], u[1], -f[1], -np.dot(u, eye)],
        [s[2], u[2], -f[2], np.dot(f, eye)],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def rotate_y(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def load_and_normalize_mesh(file_path):
    if not os.path.exists(file_path):
        mesh = trimesh.creation.torus(major_radius=0.5, minor_radius=0.2)
    else:
        mesh = trimesh.load(file_path)

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)

    # Повороты для корректной ориентации
    rot_x = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    rot_y = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])
    mesh.apply_transform(trimesh.transformations.concatenate_matrices(rot_y, rot_x))

    mesh.vertices -= mesh.center_mass
    max_scale = np.max(mesh.extents)
    if max_scale > 0:
        mesh.vertices /= max_scale

    # Генерируем нормали, если их нет
    vertices = mesh.vertices.astype(np.float32)
    normals = mesh.vertex_normals.astype(np.float32)
    faces = mesh.faces.flatten().astype(np.uint32)
    edges = mesh.edges_unique.flatten().astype(np.uint32)

    return vertices, normals, faces, edges

# ================== MAIN ==================


def main():
    MODEL_PATH = "src/_content/3D_models/laser_gun.STL"

    if not glfw.init():
        return

    window = glfw.create_window(1000, 800, "3D Shiny Metal Viewer", None, None)
    glfw.make_context_current(window)

    vertices, normals, face_indices, edge_indices = load_and_normalize_mesh(MODEL_PATH)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # VBO для вершин
    vbo_pos = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    # VBO для нормалей
    vbo_norm = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    # EBO для граней
    ebo_faces = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, face_indices.nbytes, face_indices, GL_STATIC_DRAW)

    program = create_program(
        compile_shader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compile_shader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    glEnable(GL_DEPTH_TEST)
    start_time = time.time()

    # Параметры освещения
    light_pos = np.array([2.0, 2.0, 2.0], dtype=np.float32)
    camera_pos = np.array([0.0, 0.0, 2.5], dtype=np.float32)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0.05, 0.05, 0.07, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        t = time.time() - start_time
        w, h = glfw.get_framebuffer_size(window)
        glViewport(0, 0, w, h)

        projection = ortho(-1.5 * (w / h), 1.5 * (w / h), -1.5, 1.5, -10, 10)
        view = look_at(camera_pos, np.array([0, 0, 0], dtype=np.float32), np.array([0, 1, 0], dtype=np.float32))
        model = rotate_y(t)
        mvp = projection @ view @ model

        glUseProgram(program)

        # Передача uniform-переменных
        glUniformMatrix4fv(glGetUniformLocation(program, "mvp"), 1, GL_TRUE, mvp)
        glUniformMatrix4fv(glGetUniformLocation(program, "model"), 1, GL_TRUE, model)
        glUniform3fv(glGetUniformLocation(program, "lightPos"), 1, light_pos)
        glUniform3fv(glGetUniformLocation(program, "viewPos"), 1, camera_pos)

        glBindVertexArray(vao)

        # Рисуем "Металлическое" тело
        # Цвет: темно-серый металл (0.4, 0.4, 0.45)
        glUniform3f(glGetUniformLocation(program, "objectColor"), 0.4, 0.4, 0.45)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_faces)
        glDrawElements(GL_TRIANGLES, len(face_indices), GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
