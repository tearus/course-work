import re
import matplotlib.pyplot as plt
from collections import namedtuple

import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d

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


# def get_edges(triangle: Triangle) -> list[Edge]:
#     return [
#         Edge(triangle.v1, triangle.v2),
#         Edge(triangle.v2, triangle.v3),
#         Edge(triangle.v3, triangle.v1)
#     ]


# def edge_sorted(edge: Edge) -> Edge:
#     return edge if edge.a < edge.b else Edge(edge.b, edge.a)
#
#
# def get_edges_flat(triangles: list[Triangle]) -> list[Edge]:
#     edges = [get_edges(triangle) for triangle in triangles]
#     return reduce(operator.iconcat, edges, [])


# def find_external_edges(triangles: list[Triangle]) -> list[Edge]:
#     edges = get_edges_flat(triangles)
#     sorted_edges = [edge_sorted(edge) for edge in edges]
#     unique_edges_set = {tuple(edge) for edge in sorted_edges}
#     duplicates_count = len(sorted_edges) - len(unique_edges_set)
#
#     return [edge for edge in sorted_edges if sorted_edges.count(edge) == 1] \
#         if duplicates_count > 0 \
#         else list(edges)
#
#
# def midpoint(point1: Point, point2: Point) -> Point:
#     return Point((point1.x + point2.x) / 2, (point1.y + point2.y) / 2)


def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def main():
    triangles = read_triangle_coordinates('triangle.txt')
    points = read_points_from_file('points.txt')
    center = []
    for tri in triangles:
        center.append(circumcircle(tri))

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')

    vor = Voronoi(points)
    regions, vertices = voronoi_finite_polygons_2d(vor)
    for region in regions:
        polygon = vertices[region]
        plt.fill(*zip(*polygon), alpha=0.4)
    voronoi_plot_2d(vor, ax=ax, line_colors='blue',
                    line_width=1, show_points=False, show_vertices=False)

    common_side_triangles = find_common_edges(triangles)

    for pair in common_side_triangles:
        center1 = circumcircle(pair[0])
        center2 = circumcircle(pair[1])
        plt.plot([center1.x, center2.x], [center1.y, center2.y], 'r-')
    # Отрисовка точек
    ax.scatter([p.x for p in points], [p.y for p in points], color='blue', label='Изначальные точки')

    ax.scatter([c.x for c in center], [c.y for c in center], label='Центры окружностей', color='red')

    plt.title('Диаграмма Вороного')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()

    # for edge in get_edges_flat(triangles):
    #     plt.plot([edge.a.x, edge.b.x], [edge.a.y, edge.b.y], 'g-')

    # external_edges = find_external_edges(triangles)
    # for edge in external_edges:
    #     mid = midpoint(edge.a, edge.b)
    #     for tri in triangles:
    #         if edge.a in tri and edge.b in tri:
    #             start = circumcircle(tri)
    #             plt.plot([mid.x, start.x], [mid.y, start.y], 'r--')


if __name__ == '__main__':
    main()
