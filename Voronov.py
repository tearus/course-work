import math
import operator
import re
import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
from itertools import combinations
from collections import namedtuple

Point = namedtuple('Point', 'x y')
Triangle = namedtuple('Triangle', 'v1 v2 v3')
Edge = namedtuple('Edge', 'a b')


def read_points_from_file(file_path: str) -> list[Point]:
    with open(file_path, 'r') as file:
        points = []
        for line in file.readlines():
            coordinates = line.strip()[1:-1].split(',')
            points.append(Point(int(coordinates[0]), int(coordinates[1])))
    return points


def read_triangle_coordinates(file_path: str) -> list[Triangle]:
    with open(file_path, 'r') as file:
        lines = file.readlines()

    triangles = []
    for line in lines:
        match = re.findall(r'\[(\d+), (\d+)\]', line)
        if match:
            tc = [Point(int(coord[0]), int(coord[1])) for coord in match]
            triangles.append(Triangle(tc[0], tc[1], tc[2]))
    return triangles


def circumcircle(tri: Triangle) -> Point:
    D = ((tri.v1.x - tri.v3.x) * (tri.v2.y - tri.v3.y) - (tri.v2.x - tri.v3.x) * (tri.v1.y - tri.v3.y))
    center_x = (((tri.v1.x - tri.v3.x) * (tri.v1.x + tri.v3.x) + (tri.v1.y - tri.v3.y) * (
            tri.v1.y + tri.v3.y)) / 2 * (tri.v2.y - tri.v3.y) - (
                        (tri.v2.x - tri.v3.x) * (tri.v2.x + tri.v3.x) + (tri.v2.y - tri.v3.y) * (
                        tri.v2.y + tri.v3.y)) / 2 * (tri.v1.y - tri.v3.y)) / D
    center_y = (((tri.v2.x - tri.v3.x) * (tri.v2.x + tri.v3.x) + (tri.v2.y - tri.v3.y) * (
            tri.v2.y + tri.v3.y)) / 2 * (tri.v1.x - tri.v3.x) - (
                        (tri.v1.x - tri.v3.x) * (tri.v1.x + tri.v3.x) + (tri.v1.y - tri.v3.y) * (
                        tri.v1.y + tri.v3.y)) / 2 * (tri.v2.x - tri.v3.x)) / D
    return Point(center_x, center_y)


def common_points(tri1: Triangle, tri2: Triangle) -> list[Point]:
    result = []
    if tri1.v1 == tri2.v1 or tri1.v1 == tri2.v2 or tri1.v1 == tri2.v3:
        result.append(tri1.v1)
    if tri1.v2 == tri2.v1 or tri1.v2 == tri2.v2 or tri1.v2 == tri2.v3:
        result.append(tri1.v2)
    if tri1.v3 == tri2.v1 or tri1.v3 == tri2.v2 or tri1.v3 == tri2.v3:
        result.append(tri1.v3)
    return result


def find_common_edges(triangles: list[Triangle]) -> list[tuple[Triangle, Triangle]]:
    result = []
    for tri1 in triangles:
        for tri2 in triangles:
            points = common_points(tri1, tri2)
            if len(points) == 2:
                result.append((tri1, tri2))
    return result


def get_edges(triangle: Triangle) -> list[Edge]:
    return [
        Edge(triangle.v1, triangle.v2),
        Edge(triangle.v2, triangle.v3),
        Edge(triangle.v3, triangle.v1)
    ]


def edge_sorted(edge: Edge) -> Edge:
    return edge if edge.a < edge.b else Edge(edge.b, edge.a)


def get_edges_flat(triangles: list[Triangle]) -> list[Edge]:
    edges = [get_edges(triangle) for triangle in triangles]
    return reduce(operator.iconcat, edges, [])


def find_external_edges(triangles: list[Triangle]) -> list[Edge]:
    edges = get_edges_flat(triangles)
    sorted_edges = [edge_sorted(edge) for edge in edges]
    unique_edges_set = {tuple(edge) for edge in sorted_edges}
    duplicates_count = len(sorted_edges) - len(unique_edges_set)

    return [edge for edge in sorted_edges if sorted_edges.count(edge) == 1] \
        if duplicates_count > 0 \
        else list(edges)


def midpoint(point1: Point, point2: Point) -> Point:
    return Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)


def main():
    triangles = read_triangle_coordinates('triangle.txt')
    points = read_points_from_file('points.txt')

    plt.figure(figsize=(10, 8))
    plt.scatter([p.x for p in points], [p.y for p in points], color='blue', label='Точки')
    plt.title('Визуализация точек и центров окружностей')
    plt.xlabel('X')
    plt.ylabel('Y')

    for tri in triangles:
        center = circumcircle(tri)
        plt.plot(center.x, center.y, 'ro')

    for edge in get_edges_flat(triangles):
        plt.plot([edge.a.x, edge.b.x], [edge.a.y, edge.b.y], 'g-')

    common_side_triangles = find_common_edges(triangles)
    for pair in common_side_triangles:
        center1 = circumcircle(pair[0])
        center2 = circumcircle(pair[1])
        plt.plot([center1.x, center2.x], [center1.y, center2.y], 'r-')

    external_edges = find_external_edges(triangles)
    for edge in external_edges:
        mid = midpoint(edge.a, edge.b)
        for tri in triangles:
            if edge.a in tri and edge.b in tri:
                start = circumcircle(tri)
                plt.plot([mid.x, start.x], [mid.y, start.y], 'r--')

    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
