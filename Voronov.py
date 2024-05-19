import math
import re
import matplotlib.pyplot as plt
import numpy as np


def read_points_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        points = []
        for line in lines:
            line = line.strip()
            coordinates = list(map(int, line[1:-1].split(',')))
            points.append(coordinates)
    return points


def read_triangle_coordinates(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    triangles = []
    for line in lines:
        match = re.findall(r'\[(\d+), (\d+)\]', line)
        if match:
            triangle_coords = [[int(coord[0]), int(coord[1])] for coord in match]
            triangles.append(triangle_coords)
    return triangles


def circumcircle(tri):
    D = ((tri[0][0] - tri[2][0]) * (tri[1][1] - tri[2][1]) - (tri[1][0] - tri[2][0]) * (tri[0][1] - tri[2][1]))
    center_x = (((tri[0][0] - tri[2][0]) * (tri[0][0] + tri[2][0]) + (tri[0][1] - tri[2][1]) * (
            tri[0][1] + tri[2][1])) / 2 * (tri[1][1] - tri[2][1]) - (
                        (tri[1][0] - tri[2][0]) * (tri[1][0] + tri[2][0]) + (tri[1][1] - tri[2][1]) * (
                        tri[1][1] + tri[2][1])) / 2 * (tri[0][1] - tri[2][1])) / D
    center_y = (((tri[1][0] - tri[2][0]) * (tri[1][0] + tri[2][0]) + (tri[1][1] - tri[2][1]) * (
            tri[1][1] + tri[2][1])) / 2 * (tri[0][0] - tri[2][0]) - (
                        (tri[0][0] - tri[2][0]) * (tri[0][0] + tri[2][0]) + (tri[0][1] - tri[2][1]) * (
                        tri[0][1] + tri[2][1])) / 2 * (tri[1][0] - tri[2][0])) / D
    return [center_x, center_y]


def find_common_sides(triangles):
    common_sides = []
    n = len(triangles)
    for i, tri1 in enumerate(triangles):
        for j, tri2 in enumerate(triangles):
            if i != j:
                count = 0
                for k in tri1:
                    for l in tri2:
                        if k == l:
                            count += 1
                if count == 2:
                    common_sides.append((tri1, tri2))
    return common_sides


def find_external_edges(triangles):
    all_edges = []
    for tri in triangles:
        for i in range(len(tri)):
            sr = tuple(sorted((tri[i], tri[(i + 1) % len(tri)])))
            start_point = tuple((sr[0]))
            next_point = tuple((sr[1]))
            all_edges.append((start_point, next_point))

    unique_edges_set = set(tuple(edge) for edge in all_edges)

    duplicates_count = len(all_edges) - len(unique_edges_set)

    if duplicates_count > 0:
        external_edges = [tuple(edge) for edge in all_edges if all_edges.count(edge) == 1]
    else:
        external_edges = list(all_edges)
    return external_edges


def midpoint(point1, point2):
    """Вычисляет середину между двумя точками."""
    return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2]


def normal_vector(point1, point2):
    """Вычисляет нормальный вектор к линии, соединяющей две точки."""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return [-dy, dx]


def angle_between_vectors(a, b):
    """Calculate the angle in radians between two vectors."""
    a = np.asarray(a)
    b = np.asarray(b)
    cos_theta = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return np.arccos(cos_theta)


triangles = read_triangle_coordinates('triangle.txt')
points = read_points_from_file('points.txt')

plt.figure(figsize=(10, 8))
plt.scatter([p[0] for p in points], [p[1] for p in points], color='blue', label='Точки')
plt.title('Визуализация точек и центров окружностей')
plt.xlabel('X')
plt.ylabel('Y')

for tri in triangles:
    center = circumcircle(tri)
    plt.plot(center[0], center[1], 'ro')

for tri in triangles:
    for i in range(3):
        start_point = tri[i]
        next_point = tri[(i + 1) % 3]
        plt.plot([start_point[0], next_point[0]], [start_point[1], next_point[1]], 'g-')

common_side_triangles = find_common_sides(triangles)
for pair in common_side_triangles:
    center1 = circumcircle(pair[0])
    center2 = circumcircle(pair[1])
    plt.plot([center1[0], center2[0]], [center1[1], center2[1]], 'r-')

external_edges = find_external_edges(triangles)

# Добавление кода для построения серединных перпендикуляров
for edge in external_edges:
    mid = midpoint(edge[0], edge[1])
    for tri in triangles:
        if list(edge[0]) in tri and list(edge[1]) in tri:
            start = circumcircle(tri)
    norm = normal_vector(edge[0], edge[1])
    plt.plot([mid[0], start[0]], [mid[1], start[1]], 'r--')
    new_v = [[mid[0], start[0]], [mid[1], start[1]]]

plt.legend()
plt.grid(True)
plt.show()
